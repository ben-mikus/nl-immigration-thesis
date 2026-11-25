### src/predict.py
"""
src.predict evaluates the AutoREG baseline, AR-X with Fourier
seasonality, and Random Forest models using an expanding-history
walk-forward evaluation for each country. Fitted models are loaded
from artifacts produced by src.train, and forecasts are generated
at successive forecast origins without refitting.

Workflow
--------
1. Load the training and test panels.
2. Load fitted models and selected economic predictors for each country.
3. Prepare economic predictors using historical median imputation
   and initialize the immigration history subject to publication delays.
4. Loop through each forecast origin in the test period:
    a. Construct future economic inputs using the most recently
       available values.
    b. Generate forecasts for the configured horizons.
    c. Retain forecasts whose target periods fall within the test period.
    d. Incorporate newly available immigration observations without
       refitting model parameters.
5. Save all forecasts to results/forecasts.csv for evaluation by
   src.results.

Notes
-----
Economic predictors have already been adjusted for publication delays
by src.data. AR-X uses scaled economic predictors, while Random Forest
uses unscaled predictors. Scaling parameters remain fixed throughout
evaluation.

Longer horizons contribute fewer forecasts because targets extending
beyond the test period are excluded.

Run from the repository root through ``python3 -m src.predict`` or
``make predict``. Output directories are created as needed and existing
CSVs are overwritten.
"""


import os

import joblib
import numpy as np
import pandas as pd

from . import config
from .features import VALIDATION_MONTHS
from .models.random_forest import make_features
from .utils import build_logger

logger = build_logger()


### Load initial training and test panels and restore their monthly period columns

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

train["Period"] = pd.to_datetime(train["Period"])
test["Period"] = pd.to_datetime(test["Period"])


### Loop through each country on a two-step process; prepare the evaluation data then loop through each forecasting model

all_forecasts = []

for country, country_train in train.groupby("Country"):

    # ### Prepare the country's training and test data, aligned to a monthly time index
    
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

    # X_train = country_train[exog_columns].apply(
    #     pd.to_numeric, errors="raise"
    # )
    # X_test = country_test[exog_columns].apply(
    #     pd.to_numeric, errors="raise"
    # )


    ### Load the models fitted by src.train

    baseline_wrapper = joblib.load(
        f"models/baseline_{country}.pkl"
    )
    baseline_model = baseline_wrapper._fitted_forecaster

    arx_artifact = joblib.load(
        f"models/arx_fourier_{country}.pkl"
    )
    arx_model = arx_artifact["model"]
    arx_scaler = arx_artifact["scaler"]
    arx_columns = arx_artifact["exog_columns"]


    rf_artifact = joblib.load(
        f"models/random_forest_{country}.pkl"
    )
    rf_model = rf_artifact["model"]
    rf_columns = rf_artifact["exog_columns"]

    ### Avoid parallel worker configuration warnings
    rf_model.set_params(n_jobs=1)


    # ### Reconstruct the complete country-level economic panel
    country_full = pd.concat([
        country_train,
        country_test
    ]).sort_index()

    selection_split = len(country_train) - VALIDATION_MONTHS

    def prepare_predictiors(columns):

        X = country_full[columns].apply(
            pd.to_numeric,
            errors="coerce",
        )

        X = X.replace([np.inf, -np.inf], np.nan)

        if not columns:
            return X

        ### Same historical reference period usedduring feature validation
        medians = X.iloc[:selection_split].median()

        X = X.fillna(medians)

        if X.isna().any().any():
            raise ValueError(
                f"{country}: slected economic features contain NaNs"

            )

        return X

    X_arx_available = prepare_predictiors(arx_columns)
    X_rf_available = prepare_predictiors(rf_columns)


    ### Initial forecast origin: final month of training panel
    initial_origin = y_train.index[-1]

    ### Immigration history available at the initial origin
    history = y_train.iloc[:-config.IMMIGRATION_LAG].copy()

    assert baseline_model.model.data.row_labels[-1] == history.index[-1], (
        "Baseline model and immigration history have different cutoffs."
    )

    max_horizon = max(config.FORECASTING_HORIZONS)

    ### Forecast additional steps to account for missing
    ### immigration observations at each origin
    max_steps = max_horizon + config.IMMIGRATION_LAG


    ### Loop through the successive forecast origins, making predictions for every step from one through the maximum horizon
    
    for i in range(len(y_test)):

        if (i + 1) % 10 == 0 or i == len(y_test) - 1:
            logger.info(
                "%s | Forecast origin %d/%d | Observations through %s | %d observations",
                country,
                i + 1,
                len(y_test),
                history.index[-1].strftime("%Y-%m"),
                len(history),
            )


        ### [A] Construct future economic inputs for future months on a carry-forward assumption

        # Calendar month at which this forecast is issued
        forecast_origin = initial_origin + pd.DateOffset(months=i)

        # # Latest publication-adjusted economic information
        # latest_X = X_available.loc[forecast_origin]

        # Forecast from the last available immigration observation
        future_index = pd.date_range(
            start=history.index[-1] + pd.offsets.MonthBegin(1),
            periods=max_steps,
            freq="MS",
        )

        def make_future_economics(X_available, columns):

            latest = X_available.loc[forecast_origin]

            return pd.DataFrame(
                np.repeat(
                    latest.to_numpy().reshape(1, -1),
                    repeats=max_steps,
                    axis=0
                ),
                index=future_index,
                columns=columns,
            )

        ### AR-X Inputs
        X_arx_future = make_future_economics(
            X_arx_available,
            arx_columns,
        )

        if arx_columns:
            X_arx_future_scaled = pd.DataFrame(
                arx_scaler.transform(X_arx_future),
                columns=arx_columns,
            )
        else:
            X_arx_future_scaled = None


        ### Random Forest inputs
        X_rf_future = make_future_economics(
            X_rf_available,
            rf_columns,
        )

        forecast_start = len(history)

        ### Carry forward the economic information available at the forecast origin

        # X_future = pd.DataFrame(
        #     np.repeat(
        #         latest_X.to_numpy().reshape(1, -1),
        #         repeats=max_steps,
        #         axis=0,
        #     ),
        #     index=future_index,
        #     columns=exog_columns,
        # )

        # if not X_future.empty:
        #     X_future_scaled = pd.DataFrame(
        #         scaler.transform(X_future),
        #         index=X_future.index,
        #         columns=X_future.columns,
        #     )
        # else:
        #     X_future_scaled = X_future


        # forecast_start = len(history)


        ### [B] Generate forecasts from the fitted AR-X Fourier model (receives the future standardized economic inputs)

        arx_predictions = arx_model.predict(
            start=forecast_start,
            end=forecast_start + max_steps - 1,
            exog_oos=X_arx_future_scaled,
        )


        ### [B] Generate forecasts from the fitted Random Forest model (requires an explicit recursive loop)

        rf_history = history.copy()
        rf_predictions = []

        for period in future_index:

            ### Add the month being forecast without supplying its actual value

            rf_history.loc[period] = np.nan

            rf_X_future = make_features(
                rf_history,
                X_rf_future.loc[[period]],
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
                end=forecast_start + max_steps - 1,
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

                prediction_step = (
                    horizon + config.IMMIGRATION_LAG - 1
                )

                prediction = float(predictions.iloc[prediction_step])

                all_forecasts.append({
                    "country": country,
                    "model": model_name,
                    "origin": str(forecast_origin),
                    "period": str(y_test.index[target_idx]),
                    "horizon": horizon,
                    "actual": actual,
                    "prediction": prediction,
                    "absolute error": abs(actual - prediction),
                })

    
        
        ### [E] Update model histories without refitting

        if i == len(y_test) - 1:
            continue

        # The next forecast origin is one month later.
        next_origin = forecast_origin + pd.DateOffset(months=1)

        # Latest immigration month available at the next origin.
        available_through = (
            next_origin
            - pd.DateOffset(months=config.IMMIGRATION_LAG)
        )

        # Identify the newly published immigration observation.
        new_period = history.index[-1] + pd.offsets.MonthBegin(1)

        if new_period > available_through:
            continue

        # Retrieve the observation from the original target series.
        if new_period in y_train.index:
            observed_y = y_train.loc[[new_period]]
        else:
            observed_y = y_test.loc[[new_period]]

        ### AR-X receives only its selected economic features
        observed_arx_X = X_arx_available.loc[[new_period]]

        ### Restore monthly frequency for statsmodels append()
        monthly_index = pd.date_range(
            start=new_period,
            periods=1,
            freq="MS",
        )

        observed_y.index = monthly_index
        observed_arx_X.index = monthly_index


        ### Scale the corresponding publication-adjusted economics.
        if arx_columns:

            observed_arx_X_scaled = pd.DataFrame(
                arx_scaler.transform(observed_arx_X),
                index=observed_arx_X.index,
                columns=arx_columns,
            )

        else:
            observed_arx_X_scaled = None

        # Update AutoREG without refitting.
        baseline_model = baseline_model.append(
            observed_y,
            refit=False,
        )

        # Update AR-X without refitting.
        arx_model = arx_model.append(
            observed_y,
            exog=observed_arx_X_scaled,
            refit=False,
        )

        # Update Random Forest's immigration history.
        history = pd.concat([
            history,
            observed_y,
        ])

    ### Return to the top of the loop to repeat for the next forecast origin within the current country


### Return to the top of the loop to repeat for the next country


### Save forecasts for downstream evaluation in src.results

forecasts = pd.DataFrame(all_forecasts)

os.makedirs("results", exist_ok=True)
forecasts.to_csv("results/forecasts.csv", index=False)

logger.info("Saved all country-level forecasts to results/forecasts.csv")
