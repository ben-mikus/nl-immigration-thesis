### src/predict.py
"""Generate predictions using the trained forecasting models."""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error as MAE

from . import config
from .utils import build_logger

logger = build_logger()


### Load test observations

y_test = pd.read_csv(
    "data/processed/test.csv",
    index_col=0,
    parse_dates=True
).squeeze("columns")


### Loop through the trained models, evaluating each against the forecast horizons

models = {
    "baseline": "models/baseline.pkl"
}

all_forecasts = []
all_metrics = []

for model_name, model_path in models.items():
    model = joblib.load(model_path)

    fh = np.arange(1, config.HOLDOUT_SIZE + 1)
    y_pred = model.predict(fh=fh)
    actual = y_test.to_numpy(dtype=float)
    logger.info("Generated predictions for model '%s'", model_name)


    forecast_results = pd.DataFrame(
        {
            "model": model_name,
            "period": y_test.index.astype(str),
            "actual": actual,
            "prediction": y_pred
        }
    )
    forecast_results["absolute error"] = (
        np.abs(forecast_results["prediction"] - forecast_results["actual"])
    )
    all_forecasts.append(forecast_results)

    for horizon in config.FORECASTING_HORIZONS:
        all_metrics.append(
            {
                "model": model_name,
                "horizon": horizon,
                "mae": MAE(
                    y_test.iloc[:horizon],
                    y_pred[:horizon]
                )
            }
        )


### Save evaluation metrics

os.makedirs("results", exist_ok=True)

pd.concat(all_forecasts, ignore_index=True).to_csv(
    "results/forecasts.csv",
    index=False
)
logger.info("Saved forecasts for all models to 'results/forecasts.csv'")

pd.DataFrame(all_metrics).to_csv(
    "results/metrics.csv",
    index=False
)
logger.info("Saved evaluation metrics for all models to 'results/metrics.csv'")
