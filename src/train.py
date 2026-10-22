# src/train.py
"""Train and save the forecasting models."""


import os
import warnings

import joblib
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

train = pd.read_csv("data/processed/train.csv")
train["Period"] = pd.to_datetime(train["Period"])


### Train a spearate model for each country

os.makedirs("models", exist_ok=True)

for country, country_data in train.groupby("Country"):

    ### Extract the country's immigration time series

    y_train = (
        country_data
        .sort_values("Period")
        .set_index("Period")["Immigration"]
        .asfreq("MS")
    )


    ### Fit the existing AutoREG baseline.

    model = baseline.train_baseline(y_train)


    ### Save the fitted model separately for each country

    model_path = f"models/baseline_{country}.pkl"
    joblib.dump(model, model_path)
    logger.info(f"Fitted baseline AutoREG model for {country} saved to {model_path}")
