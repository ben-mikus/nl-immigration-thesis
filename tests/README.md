# Tests

`pytest` typically discovers *any* file named `test_*.py` (or `*_test.py`).
However, this repository limits discovery to this directory 
(configured in `[tool.pytest.ini_options]` in `pyproject.toml`). To run them:

```bash
make test        # or: pytest -q
```

## What counts as a real test

Our checker (`python -m scripts.portfolio_check.check`)
looks for at least one assertion that tests *your* code, because
something like this passes while saying nothing about your code:

```python
def test_nothing():
    assert True          # always passes, tells you nothing
```

So does one that only checks a constant you wrote two lines above it. **The test
has to be able to fail**. Suppose you have written a `clean()` that is
supposed to drop duplicate rows:

```python
import pandas as pd

from src import cleaning


def test_clean_drops_exact_duplicates():
    rows = pd.DataFrame({"message": ["hello", "hello", "world"]})
    assert len(cleaning.clean(rows)) == 2
```

That one fails when `clean()` is wrong, which is the entire point. Write a test
that actually rings alarm bells if it fails.

## Fixtures

Tests should not download anything. Put a handful of sample rows from your data in
`tests/fixtures/` and read them from there. That's the one place data is allowed
in git. Keep it small, and keep it obviously sample data.
