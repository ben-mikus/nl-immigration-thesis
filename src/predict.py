### src/predict.py
"""Generate predictions using the trained forecasting models."""

import logging

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error as MAE

from . import config

logger = logging.getLogger(__name__)


models = {
    "baseline": "models/baseline.pkl"
}

for model, model_path in models.items():

    model = joblib.load(model_path)


    ### Load test observations

    y_test = pd.read_csv("data/processed/test.csv",index_col=0).squeeze("columns")


    ### Generate forecasts

    fh = np.arange(1, config.HOLDOUT_SIZE + 1)
    y_pred = model.predict(fh=fh).squeeze("columns")


    ### Evaluate forecast horizons

    results = []

    for horizon in config.FORECASTING_HORIZONS:
        results.append({
            "horizon": horizon,
            "mae": MAE(
                y_test.iloc[:horizon],
                y_pred[:horizon]
            )
        })


    ### Save evaluation metrics

    pd.DataFrame(results).to_csv(
        "results/metrics.csv",
        index=False
    )
