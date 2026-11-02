### src/split.py
"""
src.split separates the processed immigration panel into training and test sets per country based on a fixed test size.
The resulting splits are saved to the processed/ directory. The training panel is supplied to src.train. Both training
and test panels are supplied to src.predict for walk-forward evaluation and src.results for visualization.

Workflow
--------
1. Load and prepare the data from data/processed/data.csv.
2. Sort the data chronologically within each country.
3. Split the data into training and test sets based on a fixed test size per country.
4. Save the resulting splits to data/processed/train.csv and data/processed/test.csv.

Notes
-----
This module assumes that the input data from data/processed/data.csv is already clean and well-structured. It does not
validate that each country has sufficiently consecutive data or whether each country has unique period entries.

Run from the repository root using ``python3 -m src.split`` or ``make split``. Existing CSVs are overwritten.
"""


import pandas as pd

from . import config
from .utils import build_logger

logger = build_logger()


### Load the processed panel and restore it's monthly period column

data = pd.read_csv("data/processed/data.csv")
data["Period"] = pd.PeriodIndex(data["Period"], freq="M")


### Safety: Ensure observations are chronologically ordered within each country

data = data.sort_values(["Country", "Period"])


### Reserve the final TEST_SIZE observations independently for each country

test_rows = data.groupby("Country").cumcount(ascending=False) < config.TEST_SIZE

y_train = data.loc[~test_rows].copy()
y_test = data.loc[test_rows].copy()


### Save the splits to processed/

y_train.to_csv("data/processed/train.csv", index=False)
y_test.to_csv("data/processed/test.csv", index=False)

logger.info("Saved training split (%d rows) to data/processed/train.csv", len(y_train))
logger.info("Saved test split (%d rows) to data/processed/test.csv", len(y_test))
