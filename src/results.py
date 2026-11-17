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
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle

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



### Generate a six-country summary of WAPE and selected economic features

def plot_wape_summary(metrics):
    """
    Plot WAPE by country, model, and forecast horizon.

    Displays up to six countries in a 2x3 grid, with selected
    economic features alongside each model. All panels share
    the same color scale, and each country's lowest WAPE is
    highlighted. Saves the figure as PNG and PDF.
    """

    countries = [
        country for country in config.COUNTRIES
        if country in metrics["country"].unique()
    ]

    if not countries:
        raise ValueError("No country metrics available.")

    if len(countries) > 6:
        raise ValueError("The summary supports at most six countries.")

    models = {
        "baseline": "Baseline",
        "arx_fourier": "AR-X Fourier",
        "random_forest": "Random Forest",
    }

    horizons = config.FORECASTING_HORIZONS

    ### Load selected economic features from fitted model artifacts

    selected_features = {}

    for country in countries:
        selected_features[(country, "baseline")] = []

        for model_name in ["arx_fourier", "random_forest"]:
            artifact = joblib.load(
                f"models/{model_name}_{country}.pkl"
            )

            selected_features[(country, model_name)] = (
                artifact["exog_columns"]
            )

    ### Establish one shared color scale across all countries

    finite_wape = metrics["wape"].replace(
        [np.inf, -np.inf], np.nan
    ).dropna()

    if finite_wape.empty:
        raise ValueError("No valid WAPE values to plot.")

    vmin = 0
    vmax = max(float(finite_wape.max()), 1.0)

    norm = Normalize(vmin=vmin, vmax=vmax)

    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad(color="#eeeeee")

    ### Create the six-panel layout

    fig, axes = plt.subplots(
        nrows=2,
        ncols=3,
        figsize=(16, 9),
    )

    axes = axes.flatten()

    for ax, country in zip(axes, countries):

        country_metrics = metrics.loc[
            metrics["country"] == country
        ]

        matrix = (
            country_metrics
            .pivot(index="model", columns="horizon", values="wape")
            .reindex(
                index=list(models),
                columns=horizons,
            )
        )

        values = matrix.to_numpy(dtype=float)

        ax.imshow(
            np.ma.masked_invalid(values),
            cmap=cmap,
            norm=norm,
            aspect="auto",
        )

        ### Label the horizons

        ax.set_xticks(range(len(horizons)))
        ax.set_xticklabels(
            [f"{h}M" for h in horizons],
            fontsize=10,
            fontweight="bold",
        )
        ax.xaxis.tick_top()
        ax.tick_params(length=0, pad=8)

        ### Label models and their selected features

        labels = []

        for model_name, display_name in models.items():

            features = selected_features[(country, model_name)]

            if features:
                feature_text = ",\n".join(features[:3])
                if len(features) > 3:
                    feature_text += ", ..."
            else:
                feature_text = "None"

            labels.append(
                f"{display_name}\n[{feature_text}]"
            )

        ax.set_yticks(range(len(models)))
        ax.set_yticklabels(labels, fontsize=9)

        ### Annotate each cell with its WAPE percentage

        valid = values[np.isfinite(values)]
        best_wape = valid.min() if valid.size else np.nan

        for i in range(len(models)):
            for j in range(len(horizons)):

                value = values[i, j]

                if not np.isfinite(value):
                    label = "N/A"
                    text_color = "black"
                else:
                    label = f"{value:.1f}%"

                    rgba = cmap(norm(value))
                    luminance = (
                        0.2126 * rgba[0]
                        + 0.7152 * rgba[1]
                        + 0.0722 * rgba[2]
                    )
                    text_color = (
                        "white" if luminance < 0.5 else "black"
                    )

                ax.text(
                    j, i, label,
                    ha="center",
                    va="center",
                    fontsize=11,
                    fontweight="bold",
                    color=text_color,
                )

                # Highlight all configurations tied for best WAPE.
                if np.isfinite(value) and np.isclose(
                    value, best_wape
                ):
                    ax.add_patch(
                        Rectangle(
                            (j - 0.5, i - 0.5),
                            1, 1,
                            fill=False,
                            edgecolor="forestgreen",
                            linewidth=2.5,
                        )
                    )

        ### Add country title and cell borders

        ax.set_title(
            country,
            fontsize=15,
            fontweight="bold",
            color="#203a53",
            pad=38,
        )

        ax.set_xticks(
            np.arange(-0.5, len(horizons), 1),
            minor=True,
        )
        ax.set_yticks(
            np.arange(-0.5, len(models), 1),
            minor=True,
        )
        ax.grid(
            which="minor",
            color="white",
            linewidth=1.5,
        )
        ax.tick_params(which="minor", bottom=False, left=False)

        for spine in ax.spines.values():
            spine.set_visible(False)

    ### Hide panels if fewer than six countries are available

    for ax in axes[len(countries):]:
        ax.set_visible(False)

    ### Figure title, notes, and shared colorbar

    fig.suptitle(
        "Forecast Performance by Country",
        fontsize=22,
        fontweight="bold",
        y=0.98,
    )

    fig.subplots_adjust(
        left=0.11,
        right=0.98,
        top=0.82,
        bottom=0.19,
        wspace=0.50,
        hspace=0.40,
    )

    colorbar_ax = fig.add_axes([0.35, 0.095, 0.40, 0.025])

    colorbar = fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap),
        cax=colorbar_ax,
        orientation="horizontal",
    )
    colorbar.set_label("WAPE (%) — lower is better")


    ### Save both raster and vector versions

    os.makedirs("results", exist_ok=True)

    for extension in ["png"]:
        output_path = f"results/wape_summary.{extension}"

        fig.savefig(
            output_path,
            dpi=300,
            facecolor="white",
        )

        logger.info(
            "Saved WAPE summary to %s", output_path
        )

    plt.close(fig)

plot_wape_summary(metrics=metrics)