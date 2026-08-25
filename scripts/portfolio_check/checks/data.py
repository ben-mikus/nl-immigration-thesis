from __future__ import annotations

import subprocess
from pathlib import Path

from .. import config
from ..model import FAIL, PASS, SKIP, Result
from .reports import words


def tracked_files(repo: Path) -> list | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return [p for p in out.stdout.split("\0") if p]


def _whitelisted(rel: str) -> bool:
    return rel.startswith(config.DATA_WHITELIST_PREFIXES)


def check_no_raw_data(repo: Path, week: int) -> Result:
    files = tracked_files(repo)
    if files is None:
        return Result(id="no_raw_data", title="No raw data committed", status=SKIP,
                      gate=True, detail="not a git repository")

    by_extension, by_size = [], []
    for rel in files:
        if _whitelisted(rel):
            continue
        path = repo / rel
        if not path.is_file():
            continue
        if path.suffix.lower() in config.DATA_EXTENSIONS:
            by_extension.append(rel)
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > config.MAX_TRACKED_BYTES:
            by_size.append(f"{rel} ({size // 1024} KB)")

    problems = by_extension + by_size
    if problems:
        return Result(
            id="no_raw_data", title="No raw data committed", status=FAIL, gate=True,
            detail=f"{len(problems)} tracked file(s) look like data",
            evidence=problems,
            fix="Remove them from git (git rm --cached <file>), add the pattern to "
                ".gitignore, and describe where the data comes from in data/README.md "
                "with a script that fetches it. Small test fixtures belong in "
                "tests/fixtures/, which is exempt.",
        )
    return Result(id="no_raw_data", title="No raw data committed", status=PASS,
                  gate=True, detail=f"{len(files)} tracked files, none look like data")


def check_provenance(repo: Path, week: int) -> Result:
    readme = repo / config.DATA_README
    if not readme.exists():
        return Result(
            id="data_provenance", title="Data provenance documented", status=FAIL,
            detail=f"{config.DATA_README} missing",
            fix="Create data/README.md: what the dataset is, where it came from "
                "(URL or DOI), licence or terms, and how to fetch it.",
        )
    count = words(readme.read_text(encoding="utf-8", errors="replace"))
    if count < config.DATA_README_MIN_WORDS:
        return Result(
            id="data_provenance", title="Data provenance documented", status=FAIL,
            detail=f"{config.DATA_README} is {count} words",
            fix=f"Expand data/README.md to at least {config.DATA_README_MIN_WORDS} "
                "words: source, licence, retrieval date, and how to "
                "reproduce the fetch.",
        )
    return Result(id="data_provenance", title="Data provenance documented",
                  status=PASS, detail=f"{count} words")
