### src/results.py
"""Display forecast results and visualize forecast errors."""

import matplotlib.pyplot as plt
import pandas as pd

from . import config
from .utils import build_logger

logger = build_logger()


### Load saved evaluation results

metrics = pd.read_csv("results/metrics.csv")
forecasts = pd.read_csv("results/forecasts.csv")

print("\nWalk-forward forecast accuracy (MAE)")
print(metrics.to_string(index=False))


### Load historical observations

y_train = pd.read_csv(
    "data/processed/train.csv",
    index_col=0,
    parse_dates=True,
).squeeze("columns")

y_test = pd.read_csv(
    "data/processed/test.csv",
    index_col=0,
    parse_dates=True,
).squeeze("columns")

forecasts["period"] = pd.to_datetime(forecasts["period"])


### Plot actual versus predicted values by horizon

fig, axes = plt.subplots(
    nrows=len(config.FORECASTING_HORIZONS),
    ncols=1,
    figsize=(16, 12),
    sharex=True,
)

for axis, horizon in zip(axes, config.FORECASTING_HORIZONS):

    axis.plot(
        y_train.index,
        y_train,
        marker="o",
        markersize=3,
        label="Initial training data",
        color="tab:blue",
    )

    axis.plot(
        y_test.index,
        y_test,
        marker="o",
        markersize=3,
        label="Observed immigration",
        color="tab:orange",
    )

    # Select all walk-forward predictions for this horizon.
    horizon_forecasts = forecasts[
        forecasts["horizon"] == horizon
    ]

    for model_name, model_forecasts in horizon_forecasts.groupby("model"):

        model_forecasts = model_forecasts.sort_values("period")

        axis.plot(
            model_forecasts["period"],
            model_forecasts["prediction"],
            marker="o",
            markersize=3,
            label=f"{model_name} prediction",
            color="tab:green",
        )

    # Display the aggregate MAE for this horizon.
    horizon_metrics = metrics[metrics["horizon"] == horizon]

    if not horizon_metrics.empty:
        mae = horizon_metrics.iloc[0]["mae"]
        axis.set_title(f"{horizon}-Month-Ahead Forecast | MAE: {mae:,.2f}")
    else:
        axis.set_title(f"{horizon}-Month-Ahead Forecast")

    axis.set_ylabel("Immigration")
    axis.legend()

axes[-1].set_xlabel("Period")

fig.suptitle("Walk-Forward Immigration Forecasts by Horizon", fontsize=14)
plt.tight_layout()

plt.savefig("results/forecast_comparison_by_horizon.png")

logger.info(
    "Saved walk-forward forecast comparison charts to "
    "results/forecast_comparison_by_horizon.png"
)
