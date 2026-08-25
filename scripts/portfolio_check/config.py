import datetime as _dt

COURSE = "RS:R&MD"
YEAR = "2026-fall"
LAST_WEEK = 7

LAST_WEEKLY_REPORT = 6

COURSE_START = _dt.date(2026, 8, 26)


def current_week(today: _dt.date | None = None) -> int:
    today = today or _dt.date.today()
    delta = (today - COURSE_START).days
    return max(1, min(LAST_WEEK, delta // 7 + 1))

REQUIRED_SECTIONS = {
    "built": ["what i built"],
    "exploration": ["my exploration", "exploration"],
    "genai": ["use of genai", "genai", "use of ai"],
    "reflection": ["reflection"],
}

MIN_WORDS = {"built": 30, "exploration": 20, "genai": 20, "reflection": 30}

STUB_LINES = frozenset({
    '--',
    '1. task patterns (from what i asked it to do, weekly): which tasks',
    '2. key limitations encountered (from risks or misuses you noticed):',
    "3. trade-off analysis (from this week's trade-off, weeks 3+):",
    '4. principles you would keep (from responsible use, weeks 4+): what',
    '5. future intentions: how will you approach genai in your thesis, and what',
    '7 as your genai literacy synthesis. your position can change in the meantime.',
    '<https://archive.ics.uci.edu/dataset/228/sms+spam+collection>',
    '[!note] see course page for detailed information!',
    '[!tip] opted out? point at reports/genaiessay.md and summarise it in a few',
    'a diagram, a data card.',
    'ai–reproducibility connection',
    'artifact location: link to the file(s), commit(s) or folders',
    'as you may have noticed by now: this is a revision of your week-4 draft!',
    'between getting it done and understanding it. what did you do, and would you',
    'books to scrape — book titles by genre, three or more classes, a sandbox',
    'confidently wrong?',
    'covering:',
    'data',
    'deep-dives: the topics you took further, with links to the commits',
    'did you consistently delegate, which did you keep manual, and why?',
    'do it again?',
    'efficiency vs. learning: did genai save you time this week? if so, what',
    'error)? has that changed over four weeks?',
    'expected output',
    'genai literacy synthesis (see below), or a pointer to your essay',
    'hindered deep understanding?',
    "how did this week's work support reproducibility or deployment?",
    'how did your genai use (or non-use) affect the reproducibility of your work',
    'how to get it',
    'how to run:',
    'how to try it: the commands that prove it is alive, and what to expect',
    'if someone else opened your repo today, what would help them use this part?',
    'if you chose not to use genai for something: why, and what did you gain?',
    'if you have been using genai:',
    'if you have not:',
    'in addition to describing your repo, a ## genai literacy synthesis section',
    'in your gitlab repo. an artifact is anything you made: code, tests, docs,',
    'installation steps (if needed)',
    'is there a line, and can you say what it is made of?',
    'it? which of them would you keep for work nobody is grading?',
    'key tools used: e.g., docker, pytest, gitlab, etc.',
    'known limitations',
    'licence',
    'looking back, where did genai help your learning, and where might it have',
    'make sure to first write your peer review before starting this section! this',
    'might you have learned by doing it by hand?',
    'no data of your own? either of these works, and both are text classification:',
    'nothing you put in this directory is to be committed except this file. it should',
    'now? describe it honestly, without defending it yet.',
    'one moment of tension: a specific occasion where you felt the trade-off',
    'one moment of tension: a specific occasion where you wondered whether a',
    'outline instructions and background info how someone else gets the same data you',
    'peer feedback: what you changed after week 4, or why you did not',
    'reports, and this synthesis is where you pull them together.',
    'reports/genaiessay.md instead and skip this section.',
    'responsible use',
    'risks or misuses you noticed: was the output misleading? ambiguous?',
    'rules did you end up following about when to trust output and when to check',
    'run command(s)',
    'section should be about ~500 words, and it is a draft: you revise it in week',
    'sentences. the same five headings apply to your essay.',
    "should be part of that readme. that's where your reflection reports come in.",
    'site that exists to be fetched. <http://books.toscrape.com>',
    'sms spam collection — 5,574 labelled messages, two classes, cc by 4.0.',
    'snapshot: what is in this repository, with a link per piece',
    'someone else could rely on it?',
    'source',
    'summary: short description of your implementation this week.',
    'that is a complete answer. if you have opted out for the whole course, write',
    'the basics. (example: "i tried using docker compose...")',
    'the pattern: what do you lean on instead (documentation, peers, trial and',
    'the pattern: which kinds of task do you hand over, and which do you keep?',
    "this week's trade-off",
    'this week?',
    'tool would have helped, or felt glad you were not using one.',
    'two or three significant errors or corrections across the course.',
    'used (and its caveats).',
    'used it?',
    'using genai is entirely optional. if you used none this week, say so and why:',
    'wednesday 14 october, 08:00 and it is what we grade. aim for 800–1200 words',
    'what did you do to make sure you understood the output rather than just',
    'what i asked it to do: paste the prompt(s), or describe the task.',
    'what i got and did with it: what you modified, tested, or rejected.',
    'what i investigated further: choose one tool or concept and go beyond',
    'what next: realistic, scoped steps if this became a real project',
    'what principle were you following when you decided that was enough?',
    'what was most confusing, or most interesting?',
    'what you are unsure about.',
    'what you are unsure about. has watching your peers changed anything?',
    'where to look (optional): a script, an extra readme, or a branch.',
    'where you actually are: how do you use these tools in technical work right',
    'where you actually are: how has working without these tools shaped how you',
    'why these pieces matter: each one tied to a failure it prevents',
    'work? describe it, do not defend it.',
    'would the generated code need extra documentation or verification before',
    'would you tell someone starting this course next year?',
    "you've been building each item (listed below) in a specific section of your",
    'your final portfolio is your readme.md, not this file. it is due',
    '🏁 1. final portfolio',
    '💬 4. reflection',
    '📅 week 1: git & project scaffold',
    '📅 week 2: bash, make & ruff',
    '📅 week 3: testing, debugging & oop',
    '📅 week 4: environments & docker',
    '📅 week 5: data ingestion & classification',
    '📅 week 6: web deployment & model serving',
    '📅 week 7: polish & final submission',
    '🔍 2. my exploration',
    '🛠️ 1. what i built',
    '🤖 3. use of genai',
    '🧠 2. genai literacy synthesis',
    '🧭 5. your position, so far',
})

PLACEHOLDERS = [
    "short description of your implementation this week",
    "link to specific file(s), commit(s) or folder(s)",
    "paste the prompt(s), or describe the task",
    "what you modified, tested, or rejected",
    "choose one tool or concept and go beyond the basics",
]

GENAI_SUBSECTIONS = {
    "tradeoff": ["trade-off", "tradeoff", "efficiency vs"],
    "reproducibility": ["reproducibility connection", "ai-reproducibility",
                        "ai–reproducibility"],
    "responsible": ["responsible use", "responsible"],
}
MIN_WORDS_SUBSECTION = 15

OPTOUT_MARKERS = ["opted out", "opt-out", "opt out", "not use genai", "no genai"]
OPTOUT_ESSAY = "reports/genai_essay.md"
OPTOUT_ESSAY_MIN_WORDS = 800

PHILOSOPHY_REPORT = "reports/week04.md"
PHILOSOPHY_ALIASES = ["your position, so far", "your position",
                      "genai philosophy draft", "philosophy draft", "philosophy"]
PHILOSOPHY_MIN_WORDS = 250

ARTIFACT_ALIASES = ["what i built", "artifact location", "artefact location"]

FINAL_README_MIN_WORDS = 800

TEMPLATE_README_MARKERS = (
    "rs:r&md portfolio", "start here", "the weekly rhythm", "the gate",
    "two rules worth knowing on day one", "what is in here", "getting help",
    "rs-rmd-portfolio-template",
    "quick tour of the non-code files in your starter repo",
)

EXAMPLE_DEPS_FILE = "requirements.txt"
EXAMPLE_DEPS_MARKERS = ("Runtime dependency examples", "should be removed by the end")

DEPLOYMENT_STUB_MARKERS = ("Not built yet", 'st.title("My model")')
DEPLOYMENT_MIN_LINES = 10

CITATION_FILE = "CITATION.cff"
CITATION_REQUIRED = ("title", "authors")

FINAL_SYNTHESIS_FILES = ("README.md", "reports/final.md")
FINAL_SYNTHESIS_MIN_WORDS = 200
FINAL_TAG = "v1.0-final"

DATA_EXTENSIONS = {
    ".csv", ".tsv", ".psv", ".parquet", ".feather", ".arrow",
    ".xlsx", ".xls", ".db", ".sqlite", ".sqlite3",
    ".pkl", ".pickle", ".joblib", ".npy", ".npz", ".h5", ".hdf5",
    ".zip", ".gz", ".bz2", ".xz", ".tar", ".7z", ".rar",
}
MAX_TRACKED_BYTES = 1_000_000
DATA_WHITELIST_PREFIXES = ("tests/fixtures/", "reports/checks/", "docs/")

CHECKS_DIR = "reports/checks"
DATA_README = "data/README.md"
DATA_README_MIN_WORDS = 60

KEYS_DIR = "keys"
ALLOWED_KEY_TYPES = {
    "ssh-ed25519", "ssh-rsa", "ecdsa-sha2-nistp256",
    "ecdsa-sha2-nistp384", "ecdsa-sha2-nistp521",
    "sk-ssh-ed25519@openssh.com", "sk-ecdsa-sha2-nistp256@openssh.com",
}
MIN_RSA_BITS = 3072

ACTIVE_FROM = {
    "readme": 1,
    "gitignore": 1,
    "reports_present": 1,
    "reports_sections": 1,
    "artifact_links": 1,
    "check_reports": 2,
    "reports_genai": 1,
    "genai_reproducibility": 2,
    "genai_tradeoff": 3,
    "genai_responsible": 4,
    "no_raw_data": 1,
    "ssh_key": 1,
    "makefile": 2,
    "make_targets": 2,
    "scripts_dir": 2,
    "lint": 2,
    "tests_dir": 3,
    "tests_pass": 3,
    "tests_nontrivial": 3,
    "env_file": 4,
    "dockerfile": 4,
    "docker_build": 4,
    "data_provenance": 5,
    "seed": 5,
    "make_all": 5,
    "deployment": 6,
    "genai_philosophy": 4,
    "final_tag": 7,
    "final_synthesis": 7,
    "final_portfolio": 7,
    "citation": 7,
    "example_deps": 7,
}

GATE = [
    "readme",
    "reports_present",
    "reports_sections",
    "reports_genai",
    "env_file",
    "make_all",
    "tests_pass",
    "tests_nontrivial",
    "no_raw_data",
    "final_tag",
    "seed",
]

RANDOMNESS = (
    "train_test_split(", "np.random", "numpy.random", "random.choice",
    "random.sample", "random.shuffle", "random.randint", "random.random(",
    "shuffle=True", "torch.rand", "sample(",
)
SEEDS = (
    "random_state=", "random.seed(", "np.random.seed(", "numpy.random.seed(",
    "manual_seed(", "set_seed(", "seed=", "PYTHONHASHSEED",
)

SLOW = {"docker_build", "make_all"}
