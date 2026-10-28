### src/predict.py
"""Generate expanding-window walk-forward forecasts using trained forecasting models."""

import os
import warnings
from statsmodels.tools.sm_exceptions import EstimationWarning

import numpy as np
import pandas as pd

from . import config
from .models.baseline import train_baseline
# from .models.dynamic import train_dynamic
from .models.auto_fourier import train_arx_fourier
from .models.random_forest import train_random_forest, make_features
from sklearn.preprocessing import StandardScaler
from .utils import build_logger

logger = build_logger()


### Load training and test observations

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

train["Period"] = pd.to_datetime(train["Period"])
test["Period"] = pd.to_datetime(test["Period"])

exog_columns = [
    column
    for column in train.columns
    if column not in ["Country", "Period", "Immigration"]
]


### Country Loop: Perform expanding-window walk-forward validation for each country

all_forecasts = []

for country, country_train in train.groupby("Country"):

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

    scaler = StandardScaler()
    scaler.fit(X_train)

    # start_params = None


    ### Loop configuration

    history = y_train.copy()
    X_history = X_train.copy()

    max_horizon = max(config.FORECASTING_HORIZONS)
    fh = np.arange(1, max_horizon + 1)

    logger.info(f"Generating historical forecasts for {country}")


    ### Model Loop: Perform the forecasting loop for each model
    
    for i in range(len(y_test)):

        logger.info(
            "%s | Origin %d/%d | Training through %s | %d observations",
            country,
            i + 1,
            len(y_test),
            history.index[-1].strftime("%Y-%m"),
            len(history),
        )

        ### (with FutureWarnings surpressed)

        warnings.filterwarnings(
            "ignore",
            message=r"The default of config .*remember_data.*",
            category=FutureWarning,
            module=r"sktime\.forecasting\.base\._base"
        )
        warnings.filterwarnings(
            "ignore",
            category=EstimationWarning,
            module=r"statsmodels"
        )

        X_history_scaled = pd.DataFrame(
            scaler.transform(X_history),
            index=X_history.index,
            columns=X_history.columns,
        )

        baseline_model = train_baseline(history)

        # dynamic_model, seasonality = train_dynamic(
        #     history,
        #     X_history_scaled,
        # )

        # dynamic_results = dynamic_model

        # if dynamic_results.mle_retvals.get("converged", False):
        #     start_params = dynamic_results.params
        # else:
        #     logger.warning(
        #         "SARIMAX did not converge for %s at origin %s",
        #         country,
        #         i + 1
        #     )

        # fitted_models = {
        #     "baseline": baseline_model,
        #     "dynamic": dynamic_model,
        # }

        arx_model = train_arx_fourier(
            history,
            X_history_scaled,
            lags=2,
            fourier_order=3,
        )

        ### Prepare Random Forest training observations

        rf_features = make_features(history, X_history)

        # Initial observations do not have all requested lag values.
        first_row = max(config.RF_LAGS)

        rf_X_train = rf_features.iloc[first_row:]
        rf_y_train = history.iloc[first_row:]

        rf_model = train_random_forest(
            rf_y_train,
            rf_X_train,
        )


        ### Repeat the latest known predictors across future months

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

        # fourier_future = seasonality.out_of_sample(
        #     steps=max_horizon,
        # )

        # future_predictors = pd.concat(
        #     [X_future_scaled, fourier_future],
        #     axis=1,
        # )

        # predictions_by_model = {
        #     "baseline": fitted_models["baseline"].predict(fh=fh),
        #     "dynamic": fitted_models["dynamic"].get_forecast(
        #         steps=max_horizon,
        #         exog=future_predictors,
        #     ).predicted_mean,
        # }

        # The first future observation follows the final history observation.
        forecast_start = len(history)

        arx_predictions = arx_model.predict(
            start=forecast_start,
            end=forecast_start + max_horizon - 1,
            exog_oos=X_future_scaled,
        )

    ### Generate recursive Random Forest forecasts

        rf_history = history.copy()
        rf_predictions = []

        for period in future_index:

            # Add the month being forecast without supplying its actual value.
            rf_history.loc[period] = np.nan

            rf_X_future = make_features(
                rf_history,
                X_future.loc[[period]],
            )

            prediction = float(
                rf_model.predict(rf_X_future)[0]
            )

            rf_predictions.append(prediction)

            # Subsequent forecasts use this prediction as lagged immigration.
            rf_history.loc[period] = prediction

        rf_predictions = pd.Series(
            rf_predictions,
            index=future_index,
            name="prediction",
        )

        predictions_by_model = {
            "baseline": baseline_model.predict(fh=fh),
            "arx_fourier": arx_predictions,
            "random_forest": rf_predictions,
        }


        ### Record forecasts whose target observations are available

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

    
        ### Expand the training window by one observed month.

        history = pd.concat([
            history,
            y_test.iloc[i:i + 1],
        ])

        X_history = pd.concat([
            X_history,
            X_test.iloc[i:i + 1],
        ])


### Calculate aggregate MAE for each country by forecast horizon

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