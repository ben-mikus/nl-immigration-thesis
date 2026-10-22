# src/split.py
"""Splits the preprocessed immigration data into train/test sets."""

import pandas as pd

from . import config
from .utils import build_logger

logger = build_logger()


data = pd.read_csv("data/processed/data.csv")


### Prepare target series (CSV files do not preserve pandas index types)

data["Period"] = pd.PeriodIndex(data["Period"], freq="M")
y = data.set_index("Period").sort_index()["Immigration"]


### Safety: Ensure observations are chronologically ordered within each country

data = data.sort_values(["Country", "Period"])


### Reserve the test set observations for each country

test_rows = data.groupby("Country").cumcount(ascending=False) < config.TEST_SIZE

y_train = data.loc[~test_rows].copy()
y_test = data.loc[test_rows].copy()


### Save the splits to processed/

y_train.to_csv("data/processed/train.csv", index=False)
y_test.to_csv("data/processed/test.csv", index=False)

logger.info("Saved training split (%d rows) to data/processed/train.csv", len(y_train))
logger.info("Saved test split (%d rows) to data/processed/test.csv", len(y_test))