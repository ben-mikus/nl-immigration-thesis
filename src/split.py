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


### Reserve final holdout

y_train = y.iloc[:-config.TEST_SIZE]
y_test = y.iloc[-config.TEST_SIZE:]


### Save the splits to processed/

y_train.to_csv("data/processed/train.csv")
y_test.to_csv("data/processed/test.csv")

logger.info("Saved training split (%d rows) to data/processed/train.csv", len(y_train))
logger.info("Saved test split (%d rows) to data/processed/test.csv", len(y_test))