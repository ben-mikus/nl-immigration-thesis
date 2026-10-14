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


### Display MAE table

print("\nForecast accuracy (MAE)")
print(metrics.to_string(index=False))


### Load the training observations for the historical series

y_train = pd.read_csv(
    "data/processed/train.csv",
    index_col=0,
    parse_dates=True,
).squeeze("columns")

forecasts["period"] = pd.to_datetime(forecasts["period"])

actuals = forecasts.drop_duplicates("period")


fig, axes = plt.subplots(
    nrows=len(config.FORECASTING_HORIZONS),
    ncols=1,
    figsize=(16, 12),
    sharex=True,
)

for axis, horizon in zip(axes, config.FORECASTING_HORIZONS):
    horizon_actuals = actuals.iloc[:horizon]

    axis.plot(
        y_train.index,
        y_train,
        marker="o",
        markersize=3,
        label="Training data",
    )

    axis.plot(
        horizon_actuals["period"],
        horizon_actuals["actual"],
        marker="o",
        markersize=5,
        label="Holdout observations",
    )

    for model_name, model_forecasts in forecasts.groupby("model"):
        horizon_forecasts = model_forecasts.iloc[:horizon]

        axis.plot(
            horizon_forecasts["period"],
            horizon_forecasts["prediction"],
            marker="o",
            markersize=5,
            label=f"{model_name} prediction",
        )

    axis.set_title(f"{horizon}-Month-Ahead Forecast")
    axis.set_ylabel("Immigration")
    axis.legend()

axes[-1].set_xlabel("Period")
fig.suptitle("Immigration Forecasts by Horizon", fontsize=14)
plt.tight_layout()

plt.savefig("results/forecast_comparison_by_horizon.png")
logger.info(
    "Saved forecast comparison charts to "
    "results/forecast_comparison_by_horizon.png"
)