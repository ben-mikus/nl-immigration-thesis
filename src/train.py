# src/train.py
"""Train and save the forecasting models."""


import os
import joblib
import warnings
import pandas as pd

from .models import baseline
from .utils import build_logger


logger = build_logger()

warnings.filterwarnings(
    "ignore",
    message=r"The default of config .*remember_data.*",
    category=FutureWarning,
    module=r"sktime\.forecasting\.base\._base"
)


### Load the training set

y_train = pd.read_csv(
    "data/processed/train.csv",
    index_col=0,
    parse_dates=True
).squeeze("columns")

y_train = y_train.asfreq("MS")


# Train the baseline model

logger.info("Training baseline AutoREG model")
baseline = baseline.train_baseline(y_train)


### Save the trained models

os.makedirs("models", exist_ok=True)
joblib.dump(baseline, "models/baseline.pkl")
logger.info("Fitted baseline AutoREG model saved to models/baseline.pkl")
