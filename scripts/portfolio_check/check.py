from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = "scripts.portfolio_check"

from . import config
from .checks import data, keys, reports, structure, tooling
from .model import SKIP, Report, Result, render

REGISTRY = {
    "readme": structure.check_readme,
    "final_portfolio": structure.check_final_portfolio,
    "citation": structure.check_citation,
    "example_deps": structure.check_example_deps,
    "gitignore": structure.check_gitignore,
    "makefile": structure.check_makefile,
    "scripts_dir": structure.check_scripts_dir,
    "tests_dir": structure.check_tests_dir,
    "env_file": structure.check_env_file,
    "dockerfile": structure.check_dockerfile,
    "deployment": structure.check_deployment,
    "final_tag": structure.check_final_tag,
    "reports_present": reports.check_present,
    "reports_sections": reports.check_sections,
    "artifact_links": reports.check_artifact_links,
    "check_reports": reports.check_check_reports,
    "reports_genai": reports.check_genai,
    "genai_tradeoff": reports.check_genai_tradeoff,
    "genai_reproducibility": reports.check_genai_reproducibility,
    "genai_responsible": reports.check_genai_responsible,
    "genai_philosophy": reports.check_philosophy_draft,
    "final_synthesis": reports.check_final_synthesis,
    "no_raw_data": data.check_no_raw_data,
    "data_provenance": data.check_provenance,
    "ssh_key": keys.check_key,
    "lint": tooling.check_lint,
    "tests_pass": tooling.check_tests_pass,
    "tests_nontrivial": tooling.check_tests_nontrivial,
    "make_targets": tooling.check_make_targets,
    "make_all": tooling.check_make_all,
    "seed": tooling.check_seed,
    "docker_build": tooling.check_docker_build,
}

ORDER = list(config.ACTIVE_FROM)


def run(repo: Path, week: int, gate_only: bool = False, slow: bool = False) -> Report:
    report = Report(week=week, repo=str(repo))
    for check_id in ORDER:
        if check_id not in REGISTRY:
            continue
        if gate_only and check_id not in config.GATE:
            continue
        active_from = config.ACTIVE_FROM[check_id]
        if week < active_from:
            report.add(Result(id=check_id, title=_title(check_id), status=SKIP,
                              gate=check_id in config.GATE,
                              detail=f"not active until week {active_from}"))
            continue
        if check_id in config.SLOW and not slow:
            report.add(Result(id=check_id, title=_title(check_id), status=SKIP,
                              gate=check_id in config.GATE,
                              detail="slow check — add --slow to include it"))
            continue
        result = evaluate(check_id, repo, week, REGISTRY, TITLES)
        result.gate = result.gate or check_id in config.GATE
        report.add(result)
    return report


TITLES = {
    "readme": "README with run instructions",
    "check_reports": "Check reports committed",
    "final_portfolio": "README is the final portfolio",
    "citation": "Citation metadata",
    "example_deps": "Example dependencies removed",
    "gitignore": ".gitignore present",
    "makefile": "Makefile present",
    "scripts_dir": "scripts/ directory",
    "tests_dir": "tests/ with at least one test file",
    "env_file": "Environment captured",
    "dockerfile": "Dockerfile present",
    "deployment": "Deployment artefact",
    "final_tag": f"{config.FINAL_TAG} tag",
    "reports_present": "Weekly reports written",
    "reports_sections": "Report sections filled in",
    "artifact_links": "Reports link to artefacts",
    "reports_genai": "GenAI documented (or opt-out essay)",
    "genai_tradeoff": "GenAI trade-off considered",
    "genai_reproducibility": "GenAI–reproducibility connection",
    "genai_responsible": "Responsible use articulated",
    "genai_philosophy": "GenAI philosophy draft",
    "final_synthesis": "AI Literacy Synthesis",
    "no_raw_data": "No raw data committed",
    "data_provenance": "Data provenance documented",
    "ssh_key": "SSH public key submitted",
    "lint": "Code style (ruff)",
    "tests_pass": "Tests pass",
    "tests_nontrivial": "Tests assert something real",
    "make_targets": "Makefile has usable targets",
    "make_all": "`make all` runs end to end",
    "seed": "Randomness is seeded",
    "docker_build": "Docker image builds",
}


def _title(check_id: str) -> str:
    return TITLES.get(check_id, check_id)


def evaluate(check_id: str, repo: Path, week: int,
             registry: dict, titles: dict) -> Result:
    try:
        return registry[check_id](repo, week)
    except Exception as exc:
        return Result(id=check_id, title=titles.get(check_id, check_id), status=SKIP,
                      detail=f"check errored: {type(exc).__name__}: {exc}",
                      fix="This is a bug in the checker, not in your repo. "
                          "Please report it.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check this portfolio repository.")
    ap.add_argument("--week", type=int, default=None,
                    help="course week to check against "
                         "(default: derived from the date)")
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--gate", action="store_true",
                    help="only the gate criteria, as applied to the final portfolio")
    ap.add_argument("--slow", action="store_true",
                    help="include slow checks (make all, docker build)")
    ap.add_argument("--json", type=Path, default=None,
                    help="where to write the report "
                         "(default: reports/checks/weekXX.json)")
    ap.add_argument("--no-json", action="store_true", help="do not write a report")
    ap.add_argument("--quiet", action="store_true", help="only print the summary line")
    args = ap.parse_args(argv)

    week = (config.current_week() if args.week is None
            else max(1, min(args.week, config.LAST_WEEK)))
    repo = args.repo.resolve()
    report = run(repo, week, gate_only=args.gate, slow=args.slow)

    if not args.no_json:
        target = args.json or repo / "reports" / "checks" / f"week{week:02d}.json"
        report.write_json(target)

    if args.quiet:
        s = report.to_dict()["summary"]
        print(f"week {week}: {s['passed']} passed, {s['failed']} failed, "
              f"{s['skipped']} skipped")
    else:
        print(render(report, colour=sys.stdout.isatty()))
        if not args.no_json:
            rel = (args.json or Path("reports/checks") / f"week{week:02d}.json")
            print(f"  Report written to {rel} — commit it with your work.\n")

    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
