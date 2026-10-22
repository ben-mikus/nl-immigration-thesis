### src/predict.py
"""Generate expanding-window walk-forward forecasts using trained forecasting models."""

import os
import warnings

import numpy as np
import pandas as pd

from . import config
from .models.baseline import train_baseline
from .utils import build_logger

logger = build_logger()


### Load training and test observations

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

train["Period"] = pd.to_datetime(train["Period"])
test["Period"] = pd.to_datetime(test["Period"])


### Perform expanding-window walk-forward validation for each country

all_forecasts = []

for country, country_train in train.groupby("Country"):

    y_train = (
        country_train
        .sort_values("Period")
        .set_index("Period")["Immigration"]
        .asfreq("MS")
    )

    y_test = (
        test[test["Country"] == country]
        .sort_values("Period")
        .set_index("Period")["Immigration"]
        .asfreq("MS")
    )

    history = y_train.copy()

    logger.info(f"Generating historical forecasts for {country}")

    
    for i in range(len(y_test)):

        ### (with FutrueWarnings surpressed)

        warnings.filterwarnings(
            "ignore",
            message=r"The default of config .*remember_data.*",
            category=FutureWarning,
            module=r"sktime\.forecasting\.base\._base"
        )

        ### Fit AutoREG on all observations available at this origin.

        model = train_baseline(history)

        max_horizon = max(config.FORECASTING_HORIZONS)
        predictions = model.predict(
            fh=np.arange(1, max_horizon + 1)
        )

        for horizon in config.FORECASTING_HORIZONS:

            ### Only evaluate forecasts with known actual values.

            target_idx = i + horizon - 1

            if target_idx >= len(y_test):
                continue

            actual = float(y_test.iloc[target_idx])
            prediction = float(predictions.iloc[horizon - 1])

            all_forecasts.append({
                "country": country,
                "model": "baseline",
                "origin": str(history.index[-1]),
                "period": str(y_test.index[target_idx]),
                "horizon": horizon,
                "actual": actual,
                "prediction": prediction,
                "absolute error": abs(actual - prediction)
            })


        ### Expand the training window by one observed month.

        history = pd.concat([history, y_test.iloc[i:i+1]])

### Calculate aggregate MAE for each country by forecast horizon

forecasts = pd.DataFrame(all_forecasts)

metrics = (
    forecasts.groupby(["country", "model", "horizon"])
    .agg(
        mae=("absolute error", "mean"),
        n_forecasts=("absolute error", "size")
    )
    .reset_index()
)


### Save forecasts and evaluation metrics

os.makedirs("results", exist_ok=True)

forecasts.to_csv("results/forecasts.csv", index=False)
metrics.to_csv("results/metrics.csv", index=False)

logger.info("Saved all country-level forecasts and evaluation metrics")