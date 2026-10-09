# src/run/baseline.py
"""Run the baseline AutoREG model for time series forecasting."""

import numpy as np
import pandas as pd
from sktime.forecasting.auto_reg import AutoREG
from sktime.performance_metrics.forecasting import MeanAbsoluteError

from . import config


def main():

    data = pd.read_csv("data/data.csv")

    data["Period"] = pd.PeriodIndex(
        pd.to_datetime(data["Period"].astype(str), format="%Y%m"),
        freq="M"
    )

    y = data.set_index("Period").sort_index()["Immigration"]

    # Reserve final holdout
    y_train = y.iloc[:-config.HOLDOUT_SIZE]
    y_test = y.iloc[-config.HOLDOUT_SIZE:]

    # Fit once and forecast the entire holdout
    model = AutoREG(lags=config.LAGS, trend=config.TREND)
    model.fit(y_train)

    fh = np.arange(1, config.HOLDOUT_SIZE + 1)
    y_pred = model.predict(fh=fh)

    # Evaluate forecast horizons
    mae = MeanAbsoluteError()
    results = []

    for horizon in config.FORECASTING_HORIZONS:
        results.append({
            "horizon": horizon,
            "mae": mae(
                y_test.iloc[:horizon],
                y_pred[:horizon]
            )
        })

    print("\nAutoREG Baseline Results")
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    main()
