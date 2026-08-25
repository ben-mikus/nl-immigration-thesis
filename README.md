# RS:R&MD portfolio

Your portfolio for **Reproducibility & Model Deployment**. One repository that
grows over seven weeks into a small, complete, reproducible project.

> **Delete this file's contents when you make the project your own.** What
> replaces it is your README: what your project does, how to run it, and what
> you learned. It is the first thing we read when grading.

---

## Start here

```bash
python -m scripts.portfolio_check.check
```

That is the course's code checking tool: it tells you how far your repository has
progressed on the *essentials*, and what to do about each component. Not the easiest
command to remember, so week 2 we'll teach you how to shorthand to `make check`
instead. If you run it, you may notice almost everything is failing. Each
failure tells you the next concrete step.

Run it whenever you like. It writes a small report to `reports/checks/`, and
**you commit that report along with your work**. Those committed reports are the
record of your progress: they are timestamped by git, and we read them at
grading time.

## The weekly portfolio flow

Every week: lecture → practical → you extend this repo → you write
`reports/weekXX.md` → run the checker → commit and push. Lectures are on
Wednesdays, and each week's report is due the following **Wednesday at 08:00**.

| Week | Topic | What is added to the repo |
| --- | --- | --- |
| 1 | Git & project scaffold | `.gitignore`, your SSH key, `README`, `reports/week01.md`. |
| 2 | Bash, Make & Ruff | A script of your own, a `make` target, style checks passing. |
| 3 | Testing, debugging & OOP | Real tests under `tests/`, code organised into modules. |
| 4 | Environments & Docker | Pinned dependencies, a working `Dockerfile`, peer feedback. |
| 5 | Data ingestion & classification | Documented data source, a pipeline that runs end to end. |
| 6 | Web deployment & serving | A small app in `deployment/`. |
| 7 | Polish & submission | A `v1.0-final` tag, final reflection, all gates passing. |

## What's up with these gates and checks?

Eleven checks are **gate criteria**: they describe the *minimum* shape of a
reproducible project. It runs, it's tested, it can be rebuilt, it keeps
a record, and it doesn't leak data. Don't worry: each one is something the course
explicitly teaches. The checker marks them `(gate)`. To run only those, exactly as
they will be checked for your final submission, add `--gate --slow` to the command:

```bash
python -m scripts.portfolio_check.check --gate --slow
```

`--slow` includes the two checks that take minutes rather than seconds. One of
them (`make all`) is a gate criterion, so leave it in for a complete check.
Turning that command into a `make gate` target is a week-2 exercise.

The other checks indicate what we consider to be a *complete* portfolio, and you are
strongly advised to clear those as well. They count toward your grade too. However,
note that nothing stops you from submitting with uncleared checks, and if one is
still red at the end we check it by hand before it costs you anything.

**Doing the Capstone alongside this course?** These nine are also required to pass
your baseline implementation at the Midterm Review. Not blocking here; blocking
there.

## Two important rules to remember

**Raw data does not go in git.** You'll write a `.gitignore` in week 1 that keeps
`data/` out (except its README).

**Your public SSH key goes in `keys/`.** Commit `keys/<your-u-number>.pub`. That's
the key ending in `.pub`, never the one without it. We collect these to give you
GPU4EDU access. Our checker validates yours the moment you commit it. See
`keys/README.md`.

## What is in the repository template?

| Path | What it is |
| --- | --- |
| `src/` | Your code. Empty on purpose; how you organise it is part of the work. |
| `tests/` | Your tests. |
| `scripts/` | Shell automation; `portfolio_check/` is the course's checker. Leave it alone! |
| `reports/` | Weekly reports, and the check reports you commit. |
| `data/` | Not committed. Only its README is. |
| `results/` | Model artefacts and metrics. Not committed. |
| `deployment/` | Your demo app. |
| `keys/` | Your SSH public key. |
| `notebooks/` | Optional exploration. Keep the real work in `src/`. |
| `pyproject.toml` | Your dependencies go here. |
| `requirements.txt` | An example of a pinned list. Delete it once yours is in `pyproject.toml`. |
| `CITATION.cff` | How someone cites your work. Fill in the title and your name. |
