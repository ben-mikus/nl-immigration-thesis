### src/results.py
"""
src.results presents and visualizes the walk-forward evaluation produced in src.predict. It prints an accuracy table to
the terminal and creates one figure for each country-model combination that displays the observed versus predicted 
immigration over all three forecast horizons.

Workflow
-----
1. Load the saved evaluation results from src.predict.
2. Print the walk-forward forecast accuracy table to the terminal.
3. Load the historical training and test observations.
4. Loop through each country-model combination:
    a. Extract the relevant forecasts and metrics.
    b. Generate a separate figure for each forecast horizon.
    c. Plot the observed versus predicted immigration values.
    d. Annotate the plots with the corresponding MAE values.
    e. Save the figure to the results/ directory.

Notes
-----
Historical obersvations are supplied from the original trainging and test datasets produced by src.split. No models are
refit in this module and no forecasts or metrics are reclalculated.

Each horizon panel combines forecasts from successive origins. For example, the 3-month panel displays predictions made
three months before their respective target months. All input files are expected to come from the same pipeline run. The
module does not validate this consistency.

Run from the repository root through ``pythin3 -m src.results`` or ``make results``. Additionally, ``make all`` is an
option as results is the last step in the consecutive pipeline run by the ``all`` command. Existing figures are over-
written on each run.
"""


import os
import matplotlib.pyplot as plt
import pandas as pd

from . import config
from .utils import build_logger

logger = build_logger()


### Calculate country-level metrics from the forecasts saved by src.predict

forecasts = pd.read_csv("results/forecasts.csv")

def calculate_metrics(data):
    """Return MAE, WAPE (%) and forecast count for one evaluation group."""
    absolute_error = (data["actual"] - data["prediction"]).abs()
    actual_total = data["actual"].abs().sum()
    return pd.Series({
        "mae": absolute_error.mean(),
        "wape": 100 * absolute_error.sum() / actual_total
        if actual_total > 0 else float("nan"),
        "n_forecasts": len(data),
    })


metrics = (
    forecasts.groupby(["country", "model", "horizon"])
    .apply(calculate_metrics, include_groups=False)
    .reset_index()
)
metrics["n_forecasts"] = metrics["n_forecasts"].astype(int)
metrics.to_csv("results/metrics.csv", index=False, float_format="%.4f")

print("\nWalk-forward forecast accuracy by country (MAE and WAPE)")
print(metrics.to_string(
    index=False,
    formatters={"mae": "{:,.2f}".format, "wape": "{:.2f}%".format},
))


### Load observed immigration and reconstruct dates for the shared time axis

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

train["Period"] = pd.to_datetime(train["Period"])
test["Period"] = pd.to_datetime(test["Period"])
forecasts["period"] = pd.to_datetime(forecasts["period"])


### Generate a separate figure for each country-model combination

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
            wape = horizon_metrics.iloc[0]["wape"]
            title += f" | MAE: {mae:,.2f} | WAPE: {wape:.2f}%"
        axis.set_title(title)

        axis.set_title(title)
        axis.set_ylabel("Immigration")
        axis.legend()

    axes[-1, 0].set_xlabel("Period")


    ### Title and save the completed figure to the results/ directory

    fig.suptitle(
        f"Walk-Forward Immigration Forecasts: {country} | {model_name}",
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    os.makedirs(f"results/{country}", exist_ok=True)

    output_path = (
        f"results/{country}/forecast_comparison_by_horizon_"
        f"{country}_{model_name}.png"
    )

    fig.savefig(output_path)
    plt.close(fig)

    logger.info("Saved forecast chart to %s", output_path)
