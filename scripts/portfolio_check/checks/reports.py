from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .. import config
from ..model import FAIL, PASS, SKIP, Result

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
BOLD_HEADING = re.compile(r"^\s*\*\*([^*]+?)\*\*\s*:?\s*$")
SETEXT = re.compile(r"^(={3,}|-{3,})$")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")


def normalise(text: str) -> str:
    text = "".join(c for c in text if not _is_symbol(c))
    text = re.sub(r"^\s*#{1,6}\s*", "", text)
    text = re.sub(r"[*_`~]", "", text)
    text = re.sub(r"^\s*\d+[.)]?\s*", "", text.strip())
    text = re.sub(r"[:\-–—]+\s*$", "", text.strip())
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _is_symbol(char: str) -> bool:
    if ord(char) < 128:
        return False
    return unicodedata.category(char) in {"So", "Sk", "Cf", "Mn"}


def _heading_lines(lines: list) -> list:
    heads, fence = [], None
    for i, line in enumerate(lines):
        stripped = line.strip()

        if fence:
            if stripped.startswith(fence):
                fence = None
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            continue

        m = HEADING.match(line)
        if m:
            heads.append((i, len(m.group(1)), normalise(m.group(2))))
            continue

        m = BOLD_HEADING.match(line)
        if m:
            heads.append((i, 6, normalise(m.group(1))))
            continue

        if stripped and i + 1 < len(lines):
            underline = lines[i + 1].strip()
            looks_like_heading = (len(stripped) < 60
                                 and not stripped.startswith(("-", "*", ">", "|")))
            if SETEXT.match(underline) and looks_like_heading:
                level = 1 if underline[0] == "=" else 2
                heads.append((i, level, normalise(stripped)))
    return heads


def sections(markdown: str) -> dict:
    lines = markdown.splitlines()
    heads = _heading_lines(lines)

    out = {}
    for idx, (line_no, level, name) in enumerate(heads):
        end = len(lines)
        for later_no, later_level, _ in heads[idx + 1:]:
            if later_level <= level:
                end = later_no
                break
        body = "\n".join(lines[line_no + 1:end])
        out.setdefault(name, []).append(body)
    return {k: "\n".join(v) for k, v in out.items()}


def find(secs: dict, aliases: list) -> str | None:
    for name, body in secs.items():
        if any(alias in name for alias in aliases):
            return body
    return None


def _canonical(line: str) -> str:
    line = re.sub(r"^\s*#{1,6}\s*", "", line.strip())
    line = re.sub(r"^[-*+>]\s*", "", line)
    line = re.sub(r"[*_`]", "", line)
    line = re.sub(r"^\s*\[[ xX]\]\s*", "", line)
    return re.sub(r"\s+", " ", line).strip().lower()


def student_text(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines()
                     if _canonical(ln) not in config.STUB_LINES)


def words(text: str) -> int:
    text = student_text(text)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^\s*[-*+]\s*\[ \].*$", " ", text, flags=re.M)
    text = re.sub(r"^(\s*[-*+]\s*)\[[xX]\]", r"\1", text, flags=re.M)
    text = re.sub(r"\*\*[^*]+\*\*:?", " ", text)
    return len(WORD.findall(text))


def has_placeholder(text: str) -> str | None:
    low = text.lower()
    for ph in config.PLACEHOLDERS:
        if ph in low:
            return ph
    return None


def expected_reports(week: int, first: int = 1, last: int | None = None) -> list:
    return [f"reports/week{n:02d}.md"
            for n in range(first, min(week, last or week) + 1)]


def check_present(repo: Path, week: int) -> Result:
    missing = [p for p in expected_reports(week) if not (repo / p).exists()]
    weekly = expected_reports(week, last=config.LAST_WEEKLY_REPORT)
    unwritten = [p for p in weekly
                 if (repo / p).exists()
                 and words((repo / p).read_text(encoding="utf-8",
                                                errors="replace")) == 0]
    if missing:
        return Result(
            id="reports_present", title="Weekly reports written", status=FAIL,
            gate=True, detail=f"{len(missing)} missing", evidence=missing,
            fix="Add the missing file(s) under reports/, one per week, "
                "named weekXX.md.",
        )
    if unwritten:
        return Result(
            id="reports_present", title="Weekly reports written", status=FAIL,
            gate=True, detail=f"{len(unwritten)} still untouched",
            evidence=unwritten,
            fix="These are still the template we gave you. Replace the prompts "
                "with what you actually did; the file simply existing is not "
                "the point.",
        )
    return Result(
        id="reports_present", title="Weekly reports written", status=PASS,
        gate=True,
        detail=f"{len(weekly)} of {config.LAST_WEEKLY_REPORT} written",
    )


def check_sections(repo: Path, week: int) -> Result:
    problems, checked = [], 0
    for rel in expected_reports(week, last=config.LAST_WEEKLY_REPORT):
        path = repo / rel
        if not path.exists():
            continue
        checked += 1
        secs = sections(path.read_text(encoding="utf-8", errors="replace"))
        for key, aliases in config.REQUIRED_SECTIONS.items():
            if key == "genai":
                continue
            body = find(secs, aliases)
            if body is None:
                problems.append(f"{rel}: no '{aliases[0]}' heading")
                continue
            ph = has_placeholder(body)
            if ph:
                problems.append(
                    f"{rel}: '{aliases[0]}' still has template text ({ph!r})")
            elif words(body) < config.MIN_WORDS[key]:
                problems.append(
                    f"{rel}: '{aliases[0]}' has {words(body)} words, "
                    f"expected {config.MIN_WORDS[key]}+"
                )
    if not checked:
        return Result(id="reports_sections", title="Report sections filled in",
                      status=SKIP, gate=True, detail="no reports to check yet")
    if problems:
        return Result(
            id="reports_sections", title="Report sections filled in", status=FAIL,
            gate=True, detail=f"{len(problems)} issue(s)", evidence=problems,
            fix="Each report needs What I Built, My Exploration and Reflection, "
                "written in your own words. Delete the template prompts as "
                "you answer them.",
        )
    return Result(id="reports_sections", title="Report sections filled in",
                  status=PASS, gate=True, detail=f"{checked} report(s) complete")


_LINK = re.compile(
    r"\[[^\]]+\]\([^)]+\)"
    r"|https?://\S+"
    r"|`[^`\n]*[/.][^`\n]*`"
    r"|(?<![\w/])[\w.-]+/[\w./-]+"
    r"|(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])",
    re.I)


def check_artifact_links(repo: Path, week: int) -> Result:
    missing, checked = [], 0
    for rel in expected_reports(week, last=config.LAST_WEEKLY_REPORT):
        path = repo / rel
        if not path.exists():
            continue
        checked += 1
        secs = sections(path.read_text(encoding="utf-8", errors="replace"))
        body = find(secs, config.ARTIFACT_ALIASES)
        if body is None:
            missing.append(f"{rel}: no 'What I Built' section")
        elif not _LINK.search(student_text(body)):
            missing.append(f"{rel}: nothing that looks like a link or a path")
    if not checked:
        return Result(id="artifact_links", title="Reports link to artefacts",
                      status=SKIP, detail="no reports yet")
    if missing:
        return Result(
            id="artifact_links", title="Reports link to artefacts", status=FAIL,
            detail=f"{len(missing)} of {checked} report(s)", evidence=missing,
            fix="Under 'Artifact Location', point at what you built; a "
                "path like `src/train.py`, a commit "
                "hash, or a link to the file in GitLab. 'I wrote a script' is "
                "not something anyone can click on, and linking gives points "
                "under Reflection.",
        )
    return Result(id="artifact_links", title="Reports link to artefacts",
                  status=PASS, detail=f"linked in {checked} report(s)")


def check_genai(repo: Path, week: int) -> Result:
    essay = repo / config.OPTOUT_ESSAY
    if essay.exists():
        count = words(essay.read_text(encoding="utf-8", errors="replace"))
        if count < config.OPTOUT_ESSAY_MIN_WORDS:
            return Result(
                id="reports_genai", title="GenAI documented (or opt-out essay)",
                status=FAIL, gate=True,
                detail=f"{config.OPTOUT_ESSAY} is {count} words",
                fix=f"The opt-out essay should be "
                    f"{config.OPTOUT_ESSAY_MIN_WORDS}-1000 words.",
            )
        return Result(id="reports_genai", title="GenAI documented (or opt-out essay)",
                      status=PASS, gate=True,
                      detail=f"opt-out essay, {count} words")

    problems = []
    for rel in expected_reports(week, last=config.LAST_WEEKLY_REPORT):
        path = repo / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        secs = sections(text)
        body = find(secs, config.REQUIRED_SECTIONS["genai"])
        if body is None:
            problems.append(f"{rel}: no GenAI section")
            continue
        low = student_text(body).lower()
        if any(m in low for m in config.OPTOUT_MARKERS):
            continue
        ph = has_placeholder(body)
        if ph:
            problems.append(f"{rel}: GenAI section still has template text")
        elif not low.strip():
            problems.append(f"{rel}: GenAI section is unedited template")
        elif words(body) < config.MIN_WORDS["genai"]:
            problems.append(f"{rel}: GenAI section has {words(body)} words, "
                            f"expected {config.MIN_WORDS['genai']}+")
    if problems:
        return Result(
            id="reports_genai", title="GenAI documented (or opt-out essay)",
            status=FAIL, gate=True, detail=f"{len(problems)} issue(s)",
            evidence=problems,
            fix="Document what you asked GenAI for, what you changed and verified, "
                "and what it got wrong. Alternatively, state clearly that you used "
                "none this week. Opted out for the whole course? Write "
                f"{config.OPTOUT_ESSAY} instead.",
        )
    return Result(id="reports_genai", title="GenAI documented (or opt-out essay)",
                  status=PASS, gate=True, detail="documented in every report")


def check_genai_responsible(repo: Path, week: int) -> Result:
    return _subsection_check(
        repo, week, "responsible", "Responsible use articulated",
        fix="Under 'Responsible Use', say what you did to be sure you understood "
            "the output rather than just used it, and what principle told you "
            "that was enough. Used none this week? Say what you relied on instead.")


def check_philosophy_draft(repo: Path, week: int) -> Result:
    path = repo / config.PHILOSOPHY_REPORT
    if not path.exists():
        return Result(id="genai_philosophy", title="GenAI philosophy draft",
                      status=SKIP, detail=f"{config.PHILOSOPHY_REPORT} not written yet")
    body = find(sections(path.read_text(encoding="utf-8", errors="replace")),
                config.PHILOSOPHY_ALIASES)
    count = words(body) if body else 0
    if count < config.PHILOSOPHY_MIN_WORDS:
        return Result(
            id="genai_philosophy", title="GenAI philosophy draft", status=FAIL,
            detail=("section missing" if body is None else f"{count} words"),
            fix="Part 2 of this week's peer-feedback deliverable goes under "
                "'Your Position, So Far' in reports/week04.md (about 500 words): "
                "where you actually are, the pattern in what you hand over, one "
                "tension observation, and what you are unsure about. It is a "
                "draft; you revise it into your final README.",
        )
    return Result(id="genai_philosophy", title="GenAI philosophy draft",
                  status=PASS, detail=f"{count} words")


def check_final_synthesis(repo: Path, week: int) -> Result:
    for path in (repo / name for name in config.FINAL_SYNTHESIS_FILES):
        if not path.exists():
            continue
        secs = sections(path.read_text(encoding="utf-8", errors="replace"))
        body = find(secs, ["genai literacy synthesis", "ai literacy synthesis",
                           "literacy synthesis", "final reflection"])
        if body and words(body) >= config.FINAL_SYNTHESIS_MIN_WORDS:
            return Result(id="final_synthesis", title="AI Literacy Synthesis",
                          status=PASS, detail=f"{words(body)} words in {path.name}")
    return Result(
        id="final_synthesis", title="AI Literacy Synthesis", status=FAIL,
        detail="not found in " + " or ".join(config.FINAL_SYNTHESIS_FILES),
        fix="Add a 'GenAI Literacy Synthesis' section (200+ words) to your README, "
            "which is what we grade: task patterns, limitations you hit, "
            "trade-offs, and how you will approach GenAI in your thesis. It is the "
            "revision of your week-4 draft (see reports/week07.md).",
    )


def _optout(repo: Path) -> bool:
    return (repo / config.OPTOUT_ESSAY).exists()


def _subsection_check(repo: Path, week: int, key: str, title: str, fix: str) -> Result:
    if _optout(repo):
        return Result(id=f"genai_{key}", title=title, status=PASS,
                      detail="covered by the opt-out essay")

    aliases = config.GENAI_SUBSECTIONS[key]
    first = config.ACTIVE_FROM[f"genai_{key}"]
    missing, checked = [], 0
    for rel in expected_reports(week, first=first, last=config.LAST_WEEKLY_REPORT):
        path = repo / rel
        if not path.exists():
            continue
        checked += 1
        secs = sections(path.read_text(encoding="utf-8", errors="replace"))
        body = find(secs, aliases)
        if body is None:
            missing.append(f"{rel}: no '{aliases[0]}' section")
        elif words(body) < config.MIN_WORDS_SUBSECTION:
            missing.append(f"{rel}: '{aliases[0]}' has {words(body)} words, "
                           f"expected {config.MIN_WORDS_SUBSECTION}+")
    if not checked:
        return Result(id=f"genai_{key}", title=title, status=SKIP,
                      detail="no reports yet")
    if missing:
        return Result(id=f"genai_{key}", title=title, status=FAIL,
                      detail=f"{len(missing)} of {checked} report(s)",
                      evidence=missing, fix=fix)
    return Result(id=f"genai_{key}", title=title, status=PASS,
                  detail=f"answered in {checked} report(s)")


def check_genai_tradeoff(repo: Path, week: int) -> Result:
    return _subsection_check(
        repo, week, "tradeoff", "GenAI trade-off considered",
        fix="Under 'This Week's Trade-off', say whether a tool saved you time at "
            "the cost of understanding, and what you did about it. If you used "
            "none this week, say what you gained by doing it yourself.")


def check_genai_reproducibility(repo: Path, week: int) -> Result:
    return _subsection_check(
        repo, week, "reproducibility", "GenAI–reproducibility connection",
        fix="Under 'AI–Reproducibility Connection', say how your use (or non-use) "
            "affected whether someone else could re-run and trust this week's work.")


def check_check_reports(repo: Path, week: int) -> Result:
    from .data import tracked_files

    files = tracked_files(repo)
    if files is None:
        return Result(id="check_reports", title="Check reports committed",
                      status=SKIP, detail="not a git repository")

    committed = {f for f in files if f.startswith(config.CHECKS_DIR)}
    expected = [f"{config.CHECKS_DIR}/week{n:02d}.json" for n in range(1, week)]
    missing = [p for p in expected if p not in committed]

    if not expected:
        return Result(id="check_reports", title="Check reports committed",
                      status=PASS, detail="nothing due yet")
    if missing:
        return Result(
            id="check_reports", title="Check reports committed", status=FAIL,
            detail=f"{len(expected) - len(missing)} of {len(expected)} committed",
            evidence=missing,
            fix="Run the checker each week and commit what it writes into "
                "reports/checks/. They are dated, and they are how we see that "
                "your work happened over seven weeks rather than in one.",
        )
    return Result(id="check_reports", title="Check reports committed",
                  status=PASS, detail=f"{len(expected)} of {len(expected)} committed")
