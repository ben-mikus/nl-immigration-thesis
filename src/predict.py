### src/predict.py
"""
src.predict evalauates the AutoREG baseline, AR-X with Fourier terms, and Random Forest models on an expanding, walk-
forward window for each country included in the panel data. loaded from artifacts produced by src.train, and predictions
are generated at successive forecast origins without refitting.

Workflow
-----
After loading the training and test panels, evaluation repeats the following steps for each country:

1. Establish monthly target and economic predictor histories and scale the economic predictors using the initial training sample.
2. Initialize the expanding history for walk-forward validation using the training sample.
3. Loop through each forecast origin in the test sample, refitting models and generating predictions at each step.
    a. Construct future economic inputs for the forecast horizons.
    b. Generate forecasts for the specified horizons using the fitted models.
    c. Append the forecasts to the collection of all forecasts.
    d. Update the expanding history with the newly observed data from the test sample.
    e. Repeat the process for the next forecast origin until the test sample is exhausted.

After the country loop has completed for all countries in the panel dataset, aggregate MAE values are calculated by 
country and forecast horizon. Country-level predictions and metrics are then saved to results/ for use in src.results.

Notes
-----
Economic predictors are scaled to put values of different units and magnitudes onto a comparable scale. Scaling remains
fixed at its initial training-sample estimates. AR-X with Fourier uses scaled economic inputs; Random Forest does not.

Longer horizons contribute fewer forecasts as targets beyond the end of the test sample are excluded from forecasting.

Run from the repository root through ``python3 -m src.predict.py`` or ``make predict``. Outputdirectories are created as
needed and existing CSVs are overwritten.
"""


import os
import joblib

import numpy as np
import pandas as pd
from .models.random_forest import make_features

from . import config
from .utils import build_logger

logger = build_logger()


### Load initial training and test panels and restore their monthly period columns

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

train["Period"] = pd.to_datetime(train["Period"])
test["Period"] = pd.to_datetime(test["Period"])

exog_columns = [
    column
    for column in train.columns
    if column not in ["Country", "Period", "Immigration"]
]


### Loop through each country on a two-step process; prepare the evaluation data then loop through each forecasting model

all_forecasts = []

for country, country_train in train.groupby("Country"):

    ### Prepare the country's training and test data, aligned to a monthly time index
    
    country_train = (
        country_train
        .sort_values("Period")
        .set_index("Period")
        .asfreq("MS")
    )

    country_test = (
        test.loc[test["Country"] == country]
        .sort_values("Period")
        .set_index("Period")
        .asfreq("MS")
    )

    y_train = country_train["Immigration"]
    y_test = country_test["Immigration"]

    X_train = country_train[exog_columns].apply(
        pd.to_numeric, errors="raise"
    )
    X_test = country_test[exog_columns].apply(
        pd.to_numeric, errors="raise"
    )


    ### Load the models fitted by src.train

    baseline_wrapper = joblib.load(
        f"models/baseline_{country}.pkl"
    )
    baseline_model = baseline_wrapper._fitted_forecaster

    arx_artifact = joblib.load(
        f"models/arx_fourier_{country}.pkl"
    )
    arx_model = arx_artifact["model"]
    scaler = arx_artifact["scaler"]

    rf_artifact = joblib.load(
        f"models/random_forest_{country}.pkl"
    )
    rf_model = rf_artifact["model"]


    ### Initialize the history used for predictions

    history = y_train.copy()
    X_history = X_train.copy()

    max_horizon = max(config.FORECASTING_HORIZONS)

    logger.info(
        f"Generating fixed-model forecasts for {country}"
    )


    ### Loop through the successive forecast origins, making predictions for every step from one through six
    
    for i in range(len(y_test)):

        logger.info(
            "%s | Origin %d/%d | Training through %s | %d observations",
            country,
            i + 1,
            len(y_test),
            history.index[-1].strftime("%Y-%m"),
            len(history),
        )


        ### [B] Construct future economic inputs for future months on a carry-forward assumption

        future_index = pd.date_range(
            start=history.index[-1] + pd.offsets.MonthBegin(1),
            periods=max_horizon,
            freq="MS",
        )

        X_future = pd.DataFrame(
            np.repeat(
                X_history.iloc[[-1]].to_numpy(),
                repeats=max_horizon,
                axis=0,
            ),
            index=future_index,
            columns=exog_columns,
        )

        X_future_scaled = pd.DataFrame(
            scaler.transform(X_future),
            index=X_future.index,
            columns=X_future.columns,
        )


        ### (The first future observation follows the final history observation)
        
        forecast_start = len(history)


        ### [C] Generate forecasts from the fitted AR-X Fourier model (receives the future standardized economic inputs)

        arx_predictions = arx_model.predict(
            start=forecast_start,
            end=forecast_start + max_horizon - 1,
            exog_oos=X_future_scaled,
        )


        ### [C] Generate forecasts from the fitted Random Forest model (requires an explicit recursive loop)

        rf_history = history.copy()
        rf_predictions = []

        for period in future_index:

            ### Add the month being forecast without supplying its actual value

            rf_history.loc[period] = np.nan

            rf_X_future = make_features(
                rf_history,
                X_future.loc[[period]],
            )

            prediction = float(
                rf_model.predict(rf_X_future)[0]
            )

            rf_predictions.append(prediction)


            ### Subsequent forecasts use this prediction as lagged immigration

            rf_history.loc[period] = prediction

        rf_predictions = pd.Series(
            rf_predictions,
            index=future_index,
            name="prediction",
        )


        ### [C] Collect the forecast series from each model

        predictions_by_model = {
            "baseline": baseline_model.predict(
                start=forecast_start,
                end=forecast_start + max_horizon - 1,
            ),
            "arx_fourier": arx_predictions,
            "random_forest": rf_predictions,
        }


        ### [D] Record forecasts whose target observations are available

        for model_name, predictions in predictions_by_model.items():

            for horizon in config.FORECASTING_HORIZONS:

                target_idx = i + horizon - 1

                if target_idx >= len(y_test):
                    continue

                actual = float(y_test.iloc[target_idx])
                prediction = float(predictions.iloc[horizon - 1])

                all_forecasts.append({
                    "country": country,
                    "model": model_name,
                    "origin": str(history.index[-1]),
                    "period": str(y_test.index[target_idx]),
                    "horizon": horizon,
                    "actual": actual,
                    "prediction": prediction,
                    "absolute error": abs(actual - prediction),
                })

    
        
        ### [E] Update model histories without refitting

        ### Skip updating histories after the final forecast origin
        if i == len(y_test) - 1:
            continue

        observed_y = y_test.iloc[i:i + 1]
        observed_X = X_test.iloc[i:i + 1]

        ### Scale the new economic observation

        observed_X_scaled = pd.DataFrame(
            scaler.transform(observed_X),
            index=observed_X.index,
            columns=observed_X.columns,
        )

        ### Update AutoREG baseline (coefficients unchanged)

        baseline_model = baseline_model.append(
            observed_y,
            refit=False,
        )

        ### Update AR-X Fourier (coefficients unchanged)

        arx_model = arx_model.append(
            observed_y,
            exog=observed_X_scaled,
            refit=False,
        )

        ### Update history for Random Forest features

        history = pd.concat([
            history,
            observed_y,
        ])

        X_history = pd.concat([
            X_history,
            observed_X,
        ])


    ### [F] Return to the top of the loop to repeat for the next forecast origin within the current country


### Return to the top of the loop to repeat for the next country


### After forecasting for all countries, calculate aggregate MAE for each country by forecast horizon

forecasts = pd.DataFrame(all_forecasts)

metrics = (
    forecasts.groupby(["country", "model", "horizon"])
    .agg(
        mae=("absolute error", lambda x: round(x.mean(), 2)),
        n_forecasts=("absolute error", "size")
    )
    .reset_index()
)


### Save forecasts and evaluation metrics

os.makedirs("results", exist_ok=True)

forecasts.to_csv("results/forecasts.csv", index=False)
metrics.to_csv("results/metrics.csv", index=False)

logger.info("Saved all country-level forecasts and evaluation metrics")
