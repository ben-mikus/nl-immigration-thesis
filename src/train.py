# src/train.py
"""Train and save the forecasting models."""

import logging
import os

import joblib
import pandas as pd

from .models import baseline

logger = logging.getLogger(__name__)


### Load the training set

y_train = pd.read_csv("data/processed/train.csv", index_col=0, parse_dates=True)
y_train.index = pd.to_datetime(y_train.index)


# Train the baseline model

logger.info("Training baseline AutoREG model")
baseline = baseline.train_baseline(y_train)


### Save the trained models

os.makedirs("models", exist_ok=True)
joblib.dump(baseline, "models/baseline.pkl")
logger.info("Fitted baseline AutoREG model saved to models/")
