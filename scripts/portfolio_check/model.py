from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

PASS, FAIL, SKIP = "pass", "fail", "skip"

_GLYPH = {PASS: "PASS", FAIL: "FAIL", SKIP: "skip"}


@dataclass
class Result:

    id: str
    title: str
    status: str
    detail: str = ""
    fix: str = ""
    gate: bool = False
    evidence: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.status in (PASS, SKIP)


@dataclass
class Report:
    week: int
    repo: str
    results: list = field(default_factory=list)
    mode: str = "course"
    heading: str = ""

    def add(self, result: Result) -> None:
        self.results.append(result)

    @property
    def failures(self):
        return [r for r in self.results if r.status == FAIL]

    @property
    def gate_failures(self):
        return [r for r in self.failures if r.gate]

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA_VERSION,
            "mode": self.mode,
            "week": self.week,
            "repo": self.repo,
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "commit": _current_commit(Path(self.repo)),
            "summary": {
                "passed": sum(1 for r in self.results if r.status == PASS),
                "failed": len(self.failures),
                "skipped": sum(1 for r in self.results if r.status == SKIP),
                "gate_failed": len(self.gate_failures),
            },
            "results": [asdict(r) for r in self.results],
        }

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n")


def _current_commit(repo: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _symbols() -> tuple[str, str, str]:
    try:
        "✓✗·".encode(sys.stdout.encoding or "utf-8")
    except (UnicodeEncodeError, LookupError):
        return "OK", "XX", "-"
    return "✓", "✗", "·"


def render(report: Report, colour: bool = True) -> str:
    from . import config

    def paint(code, text):
        return f"\033[{code}m{text}\033[0m" if colour else text

    tick, cross, dot = _symbols()
    scheduled = [r for r in report.results
                 if r.status == SKIP and r.detail.startswith("not active until")]
    active = [r for r in report.results if r not in scheduled]

    heading = report.heading or (
        f"Portfolio check {dot} week {report.week} of {config.LAST_WEEK}")
    lines = ["", f"  {paint('1', heading)}"]

    by_week: dict[int, list] = {}
    for r in active:
        by_week.setdefault(config.ACTIVE_FROM.get(r.id, report.week), []).append(r)

    width = 74

    def wrapped(text, indent, colour_code=None, hang=0):
        out = []
        pieces = textwrap.wrap(text, width=width - len(indent),
                               break_long_words=False)
        for n, line in enumerate(pieces):
            pad = indent + (" " * hang if n else "")
            out.append(pad + (paint(colour_code, line) if colour_code else line))
        return out

    for week in sorted(by_week):
        label = f"week {week}"
        rule = "─" * max(4, width - len(label) - 5)
        lines.append("")
        lines.append(paint("90", f"  {label} {rule}"))
        for r in by_week[week]:
            mark = {PASS: paint("32", tick), FAIL: paint("31", cross)}.get(
                r.status, paint("90", dot))
            gate = paint("33", " (gate)") if r.gate else ""
            lines.append(f"   {mark}  {r.title}{gate}")
            if r.status == SKIP:
                lines.append(paint("90", f"        {r.detail}"))
                continue
            if r.detail and (r.status == FAIL or not r.evidence):
                lines += wrapped(r.detail, "        ", "90")
            if r.status == FAIL:
                shown = r.evidence[:3]
                for item in shown:
                    lines += wrapped(f"{dot} {item}", "        ", "90", hang=2)
                if len(r.evidence) > len(shown):
                    lines.append(paint("90",
                        f"        {dot} and {len(r.evidence) - len(shown)} more"))
                if r.fix:
                    body = wrapped(r.fix, "          ", "36")
                    body[0] = "        " + paint("36", "→ ") + body[0].lstrip()
                    lines += body

    s = report.to_dict()["summary"]
    lines.append("")
    lines.append(paint("90", "  " + "─" * (width - 5)))
    if not report.failures:
        lines.append(paint("32", f"  {tick}  all {s['passed']} active checks pass"))
    else:
        lines.append(
            f"  {paint('32', str(s['passed']) + ' passed')}   "
            f"{paint('31', str(s['failed']) + ' failed')}"
            + (paint("33", f"   {len(report.gate_failures)} of them gate criteria")
               if report.gate_failures else "")
        )
        if not report.gate_failures:
            lines.append(paint("90",
                "  none of these are gate criteria; they inform your grade, "
                "they do not block submission"))
    if scheduled:
        lines.append(paint("90",
            f"  {len(scheduled)} not active yet {dot} peek with "
            f"--week {config.LAST_WEEK}"))
    lines.append("")
    return "\n".join(lines)
