from __future__ import annotations

import ast
import shutil
import subprocess
from pathlib import Path

from .. import config
from ..model import FAIL, PASS, SKIP, Result

TIMEOUT_FAST = 120
TIMEOUT_SLOW = 600


def _run(cmd: list, repo: Path, timeout: int):
    try:
        return subprocess.run(cmd, cwd=str(repo), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    except (OSError, subprocess.SubprocessError):
        return None


def _tail(text: str, lines: int = 4) -> list:
    return [ln for ln in text.strip().splitlines()[-lines:] if ln.strip()]


def check_lint(repo: Path, week: int) -> Result:
    if not shutil.which("ruff"):
        return Result(id="lint", title="Code style (ruff)", status=SKIP,
                      detail="ruff not installed")
    out = _run(["ruff", "check", "."], repo, TIMEOUT_FAST)
    if out is None:
        return Result(id="lint", title="Code style (ruff)", status=SKIP,
                      detail="ruff did not complete")
    if out.returncode == 0:
        return Result(id="lint", title="Code style (ruff)", status=PASS)
    return Result(id="lint", title="Code style (ruff)", status=FAIL,
                  detail="ruff reported problems",
                  evidence=_tail(out.stdout or out.stderr),
                  fix="Run 'ruff check --fix .' and commit the result.")


def check_tests_pass(repo: Path, week: int) -> Result:
    if not shutil.which("pytest"):
        return Result(id="tests_pass", title="Tests pass", status=SKIP, gate=True,
                      detail="pytest not installed")
    out = _run(["pytest", "-q"], repo, TIMEOUT_FAST)
    if out is None:
        return Result(id="tests_pass", title="Tests pass", status=SKIP, gate=True,
                      detail="pytest did not complete")
    if out.returncode == 0:
        return Result(id="tests_pass", title="Tests pass", status=PASS, gate=True,
                      detail=_tail(out.stdout, 1)[0] if _tail(out.stdout, 1) else "")
    if out.returncode == 5:
        return Result(id="tests_pass", title="Tests pass", status=FAIL, gate=True,
                      detail="no tests collected",
                      fix="Add at least one test under tests/, named test_*.py.")
    return Result(id="tests_pass", title="Tests pass", status=FAIL, gate=True,
                  detail="pytest failed", evidence=_tail(out.stdout),
                  fix="Run 'pytest -q' locally and fix the failures.")


def check_tests_nontrivial(repo: Path, week: int) -> Result:
    tests = repo / "tests"
    files = sorted(tests.glob("test_*.py")) if tests.is_dir() else []
    if not files:
        return Result(id="tests_nontrivial", title="Tests assert something real",
                      status=FAIL, gate=True, detail="no test files",
                      fix="Add tests/test_*.py containing real assertions.")

    total, meaningful = 0, 0
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            return Result(id="tests_nontrivial", title="Tests assert something real",
                          status=FAIL, gate=True, detail=f"{path.name} does not parse",
                          fix=f"Fix the syntax error in tests/{path.name}.")
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                total += 1
                if any(isinstance(sub, (ast.Name, ast.Call, ast.Attribute,
                                        ast.Subscript, ast.Compare))
                       for sub in ast.walk(node.test)):
                    if not _all_literals(node.test):
                        meaningful += 1
    if total == 0:
        return Result(id="tests_nontrivial", title="Tests assert something real",
                      status=FAIL, gate=True, detail="no assert statements found",
                      fix="A test without an assert cannot fail. Assert on what "
                          "your code returns.")
    if meaningful == 0:
        return Result(id="tests_nontrivial", title="Tests assert something real",
                      status=FAIL, gate=True,
                      detail=f"{total} assertion(s), all on literals",
                      fix="assert True always passes. Import your own code and "
                          "assert on its output instead.")
    return Result(id="tests_nontrivial", title="Tests assert something real",
                  status=PASS, gate=True,
                  detail=f"{meaningful} of {total} assertion(s) exercise your code")


def _all_literals(node: ast.AST) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, (ast.Name, ast.Call, ast.Attribute, ast.Subscript)):
            return False
    return True


def _make_targets(repo: Path) -> set:
    makefile = repo / "Makefile"
    if not makefile.exists():
        return set()
    targets = set()
    for line in makefile.read_text(encoding="utf-8", errors="replace").splitlines():
        if any(op in line for op in (":=", "?=", "+=", "!=")):
            continue
        if line and not line.startswith(("\t", " ", "#")) and ":" in line:
            name = line.split(":", 1)[0].strip()
            if name and not name.startswith(".") and "=" not in name:
                targets.add(name)
    return targets


def check_make_targets(repo: Path, week: int) -> Result:
    targets = _make_targets(repo)
    if not targets:
        return Result(id="make_targets", title="Makefile has usable targets",
                      status=FAIL, detail="no targets found",
                      fix="Define targets in your Makefile, "
                          "e.g. 'prep:', 'test:', 'all:'.")
    return Result(id="make_targets", title="Makefile has usable targets", status=PASS,
                  detail=", ".join(sorted(targets)[:8]))


def check_make_all(repo: Path, week: int) -> Result:
    if not shutil.which("make"):
        return Result(id="make_all", title="`make all` runs end to end", status=SKIP,
                      gate=True, detail="make not installed")
    if "all" not in _make_targets(repo):
        return Result(id="make_all", title="`make all` runs end to end", status=FAIL,
                      gate=True, detail="no 'all' target",
                      fix="Add an 'all' target that runs your pipeline from start "
                          "to finish in one command.")
    out = _run(["make", "all"], repo, TIMEOUT_SLOW)
    if out is None:
        return Result(id="make_all", title="`make all` runs end to end", status=FAIL,
                      gate=True, detail="timed out",
                      fix="`make all` must finish in under 10 minutes. Shrink the "
                          "default run and make the full one opt-in.")
    if out.returncode != 0:
        return Result(id="make_all", title="`make all` runs end to end", status=FAIL,
                      gate=True, detail=f"exit code {out.returncode}",
                      evidence=_tail(out.stderr or out.stdout),
                      fix="Run 'make all' from a fresh clone and fix what breaks.")
    return Result(id="make_all", title="`make all` runs end to end", status=PASS,
                  gate=True)


def check_docker_build(repo: Path, week: int) -> Result:
    if not shutil.which("docker"):
        return Result(id="docker_build", title="Docker image builds", status=SKIP,
                      detail="docker not installed")
    out = _run(["docker", "build", "-t", "portfolio-check", "."], repo, TIMEOUT_SLOW)
    if out is None:
        return Result(id="docker_build", title="Docker image builds", status=SKIP,
                      detail="build did not complete in time")
    if out.returncode != 0:
        return Result(id="docker_build", title="Docker image builds", status=FAIL,
                      detail="build failed", evidence=_tail(out.stderr),
                      fix="Run 'docker build .' and fix the first error it reports.")
    return Result(id="docker_build", title="Docker image builds", status=PASS)


_SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", ".pytest_cache",
              ".ruff_cache", "scripts", "node_modules"}


def check_seed(repo: Path, week: int) -> Result:
    sources, seeded = [], False
    for path in sorted(repo.rglob("*.py")):
        rel = path.relative_to(repo)
        if any(part in _SKIP_DIRS for part in rel.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for marker in config.RANDOMNESS:
            if marker in text:
                sources.append(f"{rel}: {marker.rstrip('(')}")
                break
        if any(s in text for s in config.SEEDS):
            seeded = True

    if not sources:
        return Result(id="seed", title="Randomness is seeded", status=PASS,
                      gate=True, detail="nothing random to seed")
    if seeded:
        return Result(id="seed", title="Randomness is seeded", status=PASS,
                      gate=True, detail=f"{len(sources)} source(s), seeded")
    return Result(
        id="seed", title="Randomness is seeded", status=FAIL, gate=True,
        detail=f"{len(sources)} source(s) of randomness, no seed anywhere",
        evidence=sources[:5],
        fix="Set a seed so your numbers come back. `train_test_split(..., "
            "random_state=42)` is usually all it takes; `random.seed()` or "
            "`np.random.seed()` if you use those directly. Without one, the "
            "result in your report will be different next month.",
    )
