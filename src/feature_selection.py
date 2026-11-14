
"""
src.feature_selection selects economic predictors independently for each
country and forecasting model using forward selection.

The final portion of the training dataset is reserved for chronological
validation. Each candidate feature subset is evaluated using fixed model
parameters, expanding immigration history, and the configured forecast
horizons.

Features are accepted only when they improve validation MAE by at least
config.MIN_MAE_IMPROVEMENT. No test observations are used.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from . import config
from .models import arx_fourier, random_forest
from .utils import build_logger

logger = build_logger()


### Validation configuration

VALIDATION_MONTHS = 24
MIN_FEATURE_OBSERVATIONS = 12


### Prepare economic features without dropping immigration observations

def prepare_features(data, features, training_end):
    """
    Impute missing economic values using historical information.
    Medians are estimated from the initial fitting period only.
    """

    X = data[features].apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)

    if X.empty:
        return X

    fitting_X = X.iloc[:training_end]
    medians = fitting_X.median()

    # Carry previously available values forward, then fill initial gaps
    return X.ffill().fillna(medians)


### Identify candidate indicators with sufficient historical availability

def eligible_features(data, candidates, training_end):
    """
    Exclude unavailable or sparsely observed features before selection.
    """

    eligible = []

    for feature in candidates:

        if feature not in data.columns:
            continue

        series = pd.to_numeric(
            data[feature], errors="coerce"
        ).replace([np.inf, -np.inf], np.nan)

        initial = series.iloc[:training_end]

        if initial.notna().sum() < MIN_FEATURE_OBSERVATIONS:
            continue

        # Avoid selecting entirely stale indicators
        if series.iloc[training_end:].notna().sum() == 0:
            continue

        eligible.append(feature)

    return eligible


### Evaluate one feature combination

def evaluate_subset(data, model_name, features):
    """
    Fit one model and evaluate it on the final validation months.

    Returns the mean of the MAEs across forecasting horizons.
    """

    split = len(data) - VALIDATION_MONTHS

    y = data["Immigration"].astype(float)
    X = prepare_features(data, features, split)

    lag = config.IMMIGRATION_LAG

    # Fit only on immigration observations available at the first origin
    initial_history = y.iloc[:split - lag]

    if initial_history.empty:
        raise ValueError("Insufficient immigration history.")

    fitting_X = X.loc[initial_history.index]

    scaler = None

    if model_name == "arx_fourier":

        if features:
            scaler = StandardScaler()
            fitting_X = pd.DataFrame(
                scaler.fit_transform(fitting_X),
                index=fitting_X.index,
                columns=features,
            )
        else:
            fitting_X = None

        model = arx_fourier.train_arx_fourier(
            initial_history,
            fitting_X,
            lags=config.ARX_LAGS,
            fourier_order=config.ARX_FOURIER_ORDER,
        )

    elif model_name == "random_forest":

        training_features = random_forest.make_features(
            initial_history,
            fitting_X,
        )

        first_row = max(config.RF_LAGS)

        model = random_forest.train_random_forest(
            initial_history.iloc[first_row:],
            training_features.iloc[first_row:],
        )

    else:
        raise ValueError(f"Unsupported model: {model_name}")

    history = initial_history.copy()

    errors = {
        h: [] for h in config.FORECASTING_HORIZONS
    }

    max_horizon = max(config.FORECASTING_HORIZONS)

    # Validation origins run from the month before validation starts
    # through the penultimate validation month
    for i in range(VALIDATION_MONTHS):

        origin_idx = split - 1 + i
        forecast_origin = data.index[origin_idx]

        # Economic information already adjusted for publication delays
        latest_X = X.loc[forecast_origin]

        steps = max_horizon + lag

        future_index = pd.date_range(
            start=history.index[-1] + pd.offsets.MonthBegin(1),
            periods=steps,
            freq="MS",
        )

        X_future = pd.DataFrame(
            np.repeat(
                latest_X.to_numpy().reshape(1, -1),
                steps,
                axis=0,
            ),
            index=future_index,
            columns=features,
        )

        if model_name == "arx_fourier":

            if features:
                X_future_model = pd.DataFrame(
                    scaler.transform(X_future),
                    index=future_index,
                    columns=features,
                )
            else:
                X_future_model = None

            predictions = model.predict(
                start=len(history),
                end=len(history) + steps - 1,
                exog_oos=X_future_model,
            )

        else:

            rf_history = history.copy()
            predicted = []

            for period in future_index:

                rf_history.loc[period] = np.nan

                future_features = random_forest.make_features(
                    rf_history,
                    X_future.loc[[period]],
                )

                value = float(
                    model.predict(future_features)[0]
                )

                predicted.append(value)
                rf_history.loc[period] = value

            predictions = pd.Series(
                predicted,
                index=future_index,
            )

        # Evaluate only targets contained in the validation period
        for horizon in config.FORECASTING_HORIZONS:

            target_idx = split + i + horizon - 1

            if target_idx >= len(y):
                continue

            prediction_step = horizon + lag - 1

            actual = float(y.iloc[target_idx])
            forecast = float(
                predictions.iloc[prediction_step]
            )

            errors[horizon].append(abs(actual - forecast))

        # Update histories without refitting
        if i == VALIDATION_MONTHS - 1:
            continue

        next_origin = data.index[origin_idx + 1]
        available_through = (
            next_origin - pd.DateOffset(months=lag)
        )

        new_period = history.index[-1] + pd.offsets.MonthBegin(1)

        if new_period > available_through:
            continue

        observed_y = y.loc[[new_period]].asfreq("MS")
        observed_X = X.loc[[new_period]].asfreq("MS")

        if model_name == "arx_fourier":

            if features:
                observed_X_model = pd.DataFrame(
                    scaler.transform(observed_X),
                    index=observed_X.index,
                    columns=features,
                )
            else:
                observed_X_model = None

            model = model.append(
                observed_y,
                exog=observed_X_model,
                refit=False,
            )

        history = pd.concat([history, observed_y])

    horizon_maes = [
        np.mean(values)
        for values in errors.values()
        if values
    ]

    if len(horizon_maes) != len(config.FORECASTING_HORIZONS):
        raise ValueError("Insufficient validation forecasts.")

    return float(np.mean(horizon_maes))


### Perform forward feature selection

def select_features(country, model_name, country_data, candidates):
    """
    Select economic features using greedy forward selection.

    Returns
    -------
    selected : list[str]
        Economic features accepted for the country-model combination.
    history : list[dict]
        Validation scores and accepted features at each selection step.
    """

    data = (
        country_data
        .sort_values("Period")
        .set_index("Period")
        .asfreq("MS")
        .copy()
    )

    if data["Immigration"].isna().any():
        raise ValueError(
            f"{country}: missing immigration observations"
        )

    split = len(data) - VALIDATION_MONTHS

    if split <= max(config.RF_LAGS) + 24:
        raise ValueError(
            f"{country}: insufficient data for feature selection"
        )

    available = eligible_features(
        data,
        candidates,
        split,
    )

    # Evaluate the economic-free specification first
    best_mae = evaluate_subset(
        data,
        model_name,
        [],
    )

    selected = []

    history = [{
        "step": 0,
        "feature": None,
        "mae": best_mae,
    }]

    logger.info(
        "%s | %s | Initial validation MAE: %.2f",
        country,
        model_name,
        best_mae,
    )

    for step in range(1, config.MAX_SELECTED_FEATURES + 1):

        best_candidate = None
        candidate_mae = best_mae

        for feature in available:

            if feature in selected:
                continue

            proposed = selected + [feature]

            mae = evaluate_subset(
                data,
                model_name,
                proposed,
            )

            if mae < candidate_mae:
                candidate_mae = mae
                best_candidate = feature

        improvement = best_mae - candidate_mae

        if (
            best_candidate is None
            or improvement < config.MIN_MAE_IMPROVEMENT
        ):
            break

        selected.append(best_candidate)
        best_mae = candidate_mae

        history.append({
            "step": step,
            "feature": best_candidate,
            "mae": best_mae,
        })

        logger.info(
            "%s | %s | Selected %s | MAE: %.2f",
            country,
            model_name,
            best_candidate,
            best_mae,
        )

    logger.info(
        "%s | %s | Final selected features: %s",
        country,
        model_name,
        selected,
    )

    return selected, history
