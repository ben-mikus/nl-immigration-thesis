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

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

train["Period"] = pd.to_datetime(train["Period"])
test["Period"] = pd.to_datetime(test["Period"])
forecasts["period"] = pd.to_datetime(forecasts["period"])


### Generate a separate figure for each country

for (country, model_name), model_forecasts in forecasts.groupby(
    ["country", "model"]
):

    country_train = (
        train.loc[train["Country"] == country]
        .sort_values("Period")
    )
    country_test = (
        test.loc[test["Country"] == country]
        .sort_values("Period")
    )

    model_metrics = metrics.loc[
        (metrics["country"] == country)
        & (metrics["model"] == model_name)
    ]


    ### Plot actual versus predicted values by horizon

    horizons = config.FORECASTING_HORIZONS

    fig, axes = plt.subplots(
        nrows=len(horizons),
        ncols=1,
        figsize=(16, 4 * len(horizons)),
        sharex=True,
        squeeze=False,
    )

    for axis, horizon in zip(axes[:, 0], horizons):

        axis.plot(
            country_train["Period"],
            country_train["Immigration"],
            marker="o",
            markersize=3,
            label="Initial training data",
            color="tab:blue",
        )

        axis.plot(
            country_test["Period"],
            country_test["Immigration"],
            marker="o",
            markersize=3,
            label="Observed immigration",
            color="tab:orange",
        )

        horizon_forecasts = (
            model_forecasts.loc[
                model_forecasts["horizon"] == horizon
            ]
            .sort_values("period")
        )

        axis.plot(
            horizon_forecasts["period"],
            horizon_forecasts["prediction"],
            marker="o",
            markersize=3,
            label=f"{model_name} prediction",
            color="tab:green",
        )

        horizon_metrics = model_metrics.loc[
            model_metrics["horizon"] == horizon
        ]

        title = f"{horizon}-Month-Ahead Forecast"

        if not horizon_metrics.empty:
            mae = horizon_metrics.iloc[0]["mae"]
            title += f" | MAE: {mae:,.2f}"

        axis.set_title(title)
        axis.set_ylabel("Immigration")
        axis.legend()

    axes[-1, 0].set_xlabel("Period")

    fig.suptitle(
        f"Walk-Forward Immigration Forecasts: {country} | {model_name}",
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    output_path = (
        f"results/forecast_comparison_by_horizon_"
        f"{country}_{model_name}.png"
    )

    fig.savefig(output_path)
    plt.close(fig)

    logger.info("Saved forecast chart to %s", output_path)
