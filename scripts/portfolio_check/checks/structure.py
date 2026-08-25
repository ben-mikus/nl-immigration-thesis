from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .. import config
from ..model import FAIL, PASS, Result
from .reports import find, sections, words

ENV_FILES = ["pyproject.toml", "requirements.txt", "environment.yml", "uv.lock"]


def _exists(repo: Path, *names: str):
    return [n for n in names if (repo / n).exists()]


def check_readme(repo: Path, week: int) -> Result:
    path = repo / "README.md"
    if not path.exists():
        return Result(id="readme", title="README with run instructions", status=FAIL,
                      gate=True, detail="README.md missing",
                      fix="Add a README.md describing what the project does "
                          "and how to run it.")
    text = path.read_text(encoding="utf-8", errors="replace")
    secs = sections(text)

    leftover = sorted(set(secs) & set(config.TEMPLATE_README_MARKERS))
    if len(leftover) >= 2:
        return Result(
            id="readme", title="README with run instructions", status=FAIL,
            gate=True, detail=f"still the template's: {', '.join(leftover[:4])}",
            fix="Replace the template's README with your own. Describe what this "
                "project is, and how someone else runs it. It is the first thing "
                "we read, and in week 7 it describes the portfolio itself.",
        )

    howto = find(secs, ["how to run", "how to try", "usage", "quickstart",
                        "quick start", "getting started", "start here",
                        "running", "how to use"])
    has_commands = howto is not None and "```" in howto
    if howto is None or (not has_commands and words(howto) < 15):
        return Result(
            id="readme", title="README with run instructions", status=FAIL, gate=True,
            detail="no usable 'how to run' section",
            fix="Add a 'How to run' section to your README with the exact commands "
                "someone else would type from a fresh clone.",
        )
    return Result(id="readme", title="README with run instructions", status=PASS,
                  gate=True, detail=f"{words(text)} words")


def check_final_portfolio(repo: Path, week: int) -> Result:
    from .reports import sections, words

    path = repo / "README.md"
    if not path.exists():
        return Result(id="final_portfolio", title="README is the final portfolio",
                      status=FAIL, detail="README.md missing")

    text = path.read_text(encoding="utf-8", errors="replace")
    headings = set(sections(text))
    leftover = sorted(headings & set(config.TEMPLATE_README_MARKERS))
    count = words(text)

    problems = []
    if len(leftover) >= 2:
        problems.append(
            f"still has the template's own headings: {', '.join(leftover[:4])}")
    if count < config.FINAL_README_MIN_WORDS:
        problems.append(f"{count} words, expected {config.FINAL_README_MIN_WORDS}+")

    if problems:
        return Result(
            id="final_portfolio", title="README is the final portfolio",
            status=FAIL, detail="; ".join(problems),
            fix="Your README *is* the portfolio we grade: 800–1200 words, due "
                "soon after the lectures end. Replace the template's text "
                "with yours: what the project is, how to try it, why the pieces "
                "matter, what you explored, what changed after peer feedback, "
                "your GenAI Literacy Synthesis, and what you would do next.",
        )
    return Result(id="final_portfolio", title="README is the final portfolio",
                  status=PASS, detail=f"{count} words, template text replaced")


def _cff(text: str) -> dict:
    data, key = {}, None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t", "-")):
            if key:
                if not isinstance(data.get(key), list):
                    data[key] = []
                data[key].append(raw.strip().lstrip("- "))
            continue
        name, sep, value = raw.partition(":")
        if not sep:
            continue
        key = name.strip()
        data[key] = value.strip().strip('"').strip("'")
    return data


def check_citation(repo: Path, week: int) -> Result:
    path = repo / config.CITATION_FILE
    if not path.exists():
        return Result(
            id="citation", title="Citation metadata", status=FAIL,
            detail=f"{config.CITATION_FILE} missing",
            fix="Restore CITATION.cff and fill in the title and your name. It is "
                "how anyone credits this work, including you in a thesis.",
        )

    data = _cff(path.read_text(encoding="utf-8", errors="replace"))
    if "cff-version" not in data:
        return Result(
            id="citation", title="Citation metadata", status=FAIL,
            detail="no cff-version — this does not parse as a citation file",
            fix="A CITATION.cff is YAML, not text. Keep `cff-version`, `title` "
                "and `authors`. Format: https://citation-file-format.github.io",
        )

    empty = [k for k in config.CITATION_REQUIRED if not data.get(k)]
    if empty:
        return Result(
            id="citation", title="Citation metadata", status=FAIL,
            detail="still the placeholders: "
                   + ", ".join(f"{k} is empty" for k in empty),
            fix="Fill in `title` and `authors` in CITATION.cff; the name of your "
                "project and your own name. It ships blank on purpose.",
        )
    authors = data["authors"]
    who = authors[0] if isinstance(authors, list) else authors
    return Result(id="citation", title="Citation metadata", status=PASS,
                  detail=f"{data['title']} — {who}")


def check_example_deps(repo: Path, week: int) -> Result:
    path = repo / config.EXAMPLE_DEPS_FILE
    if not path.exists():
        return Result(id="example_deps", title="Example dependencies removed",
                      status=PASS, detail=f"{config.EXAMPLE_DEPS_FILE} removed")

    text = path.read_text(encoding="utf-8", errors="replace")
    if any(m in text for m in config.EXAMPLE_DEPS_MARKERS):
        return Result(
            id="example_deps", title="Example dependencies removed", status=FAIL,
            detail=f"{config.EXAMPLE_DEPS_FILE} is still the shipped example",
            fix="Your dependencies belong in pyproject.toml. Delete "
                "requirements.txt. Nothing needs it any more; the Dockerfile "
                "and `make install` both read pyproject.toml.",
        )
    return Result(id="example_deps", title="Example dependencies removed",
                  status=PASS, detail=f"{config.EXAMPLE_DEPS_FILE} is yours, not ours")


def check_gitignore(repo: Path, week: int) -> Result:
    path = repo / ".gitignore"
    if not path.exists():
        return Result(id="gitignore", title=".gitignore present", status=FAIL,
                      detail="missing",
                      fix="Add a .gitignore. At minimum ignore data/ (except its "
                          "README), .venv/ and __pycache__/.")
    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"^\s*data/", text, re.M):
        return Result(
            id="gitignore", title=".gitignore present", status=FAIL,
            detail="no data/ rule",
            fix="Add 'data/*' and '!data/README.md'; raw data should stay out of git.",
        )
    return Result(id="gitignore", title=".gitignore present", status=PASS,
                  detail="includes a data/ rule")


def check_makefile(repo: Path, week: int) -> Result:
    if not (repo / "Makefile").exists():
        return Result(id="makefile", title="Makefile present", status=FAIL,
                      detail="missing",
                      fix="Add a Makefile so one command runs each step.")
    return Result(id="makefile", title="Makefile present", status=PASS)


def check_scripts_dir(repo: Path, week: int) -> Result:
    scripts = repo / "scripts"
    if not scripts.is_dir():
        return Result(id="scripts_dir", title="scripts/ directory", status=FAIL,
                      detail="missing",
                      fix="Create scripts/ and put your shell automation there.")
    own = [p.name for p in scripts.iterdir()
           if p.is_file() and p.name != "portfolio_check"]
    if not own:
        return Result(id="scripts_dir", title="scripts/ directory", status=FAIL,
                      detail="empty",
                      fix="Add at least one script of your own, "
                          "e.g. scripts/prep_data.sh.")
    return Result(id="scripts_dir", title="scripts/ directory", status=PASS,
                  detail=f"{len(own)} script(s)")


def check_tests_dir(repo: Path, week: int) -> Result:
    tests = repo / "tests"
    files = sorted(tests.glob("test_*.py")) if tests.is_dir() else []
    if not files:
        return Result(id="tests_dir", title="tests/ with at least one test file",
                      status=FAIL, detail="none found",
                      fix="Create tests/test_something.py with a real test.")
    return Result(id="tests_dir", title="tests/ with at least one test file",
                  status=PASS, detail=f"{len(files)} file(s)")


def _declares_dependencies(repo: Path, name: str) -> bool:
    try:
        text = (repo / name).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if name == "pyproject.toml":
        block = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text,
                          re.S | re.M)
        return bool(block and block.group(1).strip().strip(","))
    if name == "environment.yml":
        return bool(re.search(r"^\s*-\s+\S", text, re.M))
    if name == config.EXAMPLE_DEPS_FILE and any(
            m in text for m in config.EXAMPLE_DEPS_MARKERS):
        return False
    return any(ln.strip() and not ln.strip().startswith("#")
               for ln in text.splitlines())


def check_env_file(repo: Path, week: int) -> Result:
    found = _exists(repo, *ENV_FILES)
    declaring = [f for f in found if _declares_dependencies(repo, f)]
    if not declaring:
        detail = ("no dependency file" if not found
                  else f"{', '.join(found)} present but declares nothing")
        return Result(id="env_file", title="Environment captured", status=FAIL,
                      gate=True, detail=detail,
                      fix="List what your project needs to run, with versions. "
                          "`dependencies = [...]` in pyproject.toml is the one "
                          "this course uses; requirements.txt or "
                          "environment.yml also count.")
    return Result(id="env_file", title="Environment captured", status=PASS,
                  gate=True, detail=", ".join(declaring))


def check_dockerfile(repo: Path, week: int) -> Result:
    if not (repo / "Dockerfile").exists():
        return Result(id="dockerfile", title="Dockerfile present", status=FAIL,
                      detail="missing",
                      fix="Add a Dockerfile that builds and runs your pipeline.")
    return Result(id="dockerfile", title="Dockerfile present", status=PASS)


def _is_stub_app(text: str) -> bool:
    return any(m in text for m in config.DEPLOYMENT_STUB_MARKERS)


def check_deployment(repo: Path, week: int) -> Result:
    folder = next((repo / n for n in ("deployment", "demo", "app")
                   if (repo / n).is_dir()), None)
    if folder is None:
        return Result(id="deployment", title="Deployment artefact", status=FAIL,
                      detail="no deployment/ directory",
                      fix="Add deployment/ with your Streamlit or FastAPI app.")

    apps = sorted(p for p in folder.rglob("*.py") if "__pycache__" not in p.parts)
    if not apps:
        return Result(id="deployment", title="Deployment artefact", status=FAIL,
                      detail=f"{folder.name}/ is empty",
                      fix="Put your app in there; the demo someone runs to "
                          "see your model do something.")

    best, best_lines = None, 0
    for path in apps:
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(m in text for m in config.DEPLOYMENT_STUB_MARKERS):
            continue
        body = [ln for ln in text.splitlines()
                if ln.strip() and not ln.strip().startswith("#")]
        if len(body) > best_lines:
            best, best_lines = path.relative_to(repo), len(body)

    if best is None:
        return Result(
            id="deployment", title="Deployment artefact", status=FAIL,
            detail="still the stub that ships with the template",
            fix="Build the demo: load what `make all` produced and let someone "
                "try it. A title and 'Not built yet' is the placeholder, not "
                "the week-6 deliverable.",
        )
    if best_lines < config.DEPLOYMENT_MIN_LINES:
        return Result(
            id="deployment", title="Deployment artefact", status=FAIL,
            detail=f"{best} is {best_lines} lines",
            fix="It should load your model and do something with input. Under "
                f"{config.DEPLOYMENT_MIN_LINES} lines is a sketch.",
        )
    return Result(id="deployment", title="Deployment artefact", status=PASS,
                  detail=f"{best}, {best_lines} lines")


def check_final_tag(repo: Path, week: int) -> Result:
    try:
        out = subprocess.run(["git", "-C", str(repo), "tag", "--list"],
                             capture_output=True, text=True, timeout=15)
        tags = out.stdout.split()
    except (OSError, subprocess.SubprocessError):
        tags = []
    if config.FINAL_TAG in tags:
        return Result(id="final_tag", title=f"{config.FINAL_TAG} tag", status=PASS,
                      gate=True)
    return Result(
        id="final_tag", title=f"{config.FINAL_TAG} tag", status=FAIL, gate=True,
        detail="not found", evidence=tags[:5],
        fix=f"Tag your submission: git tag {config.FINAL_TAG} && "
            f"git push origin {config.FINAL_TAG}",
    )
