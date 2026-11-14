### src/train.py
"""
src.train fits and saves forecasting models for each country-model combination. This module consumes the training panel
produced by src.split and fits an autoregressive baseline, an AR-X model with Fourier seasonality, and a Random Forest 
regressor model for each country. The fitted models are saved as .pkl artifacts and subsequently loaded by src.predict
for walk-forward evaluation without refitting.

Workflow
--------
1. Load the training panel from data/processed/train.csv.
2. Identify the target and predictor columns.
3. For each country:
   a. Prepare a monthly time index.
   b. Fit and save the baseline AutoREG model.
   c. Scale predictors and fit the AR-X model with Fourier terms.
   d. Fit the Random Forest regressor.
4. Save all models to the models/ directory.

Notes
-----
Every column other than Country, Period, and Immigration is treated as an economic predictor. The module assumes that
the training panel is clean, well-structured, and does not impute missing observations or explicitly validate monthly 
continuity.

Run from the repository root through ``python -m src.train`` or ``make train``. Output directories are created as needed
and existing CSVs are overwritten.
"""


import warnings

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from . import config
from .feature_selection import (
    VALIDATION_MONTHS,
    prepare_features,
    select_features,
)
from .models import arx_fourier, baseline, random_forest
from .utils import build_logger

logger = build_logger()

warnings.filterwarnings(
    "ignore",
    message=r"The default of config .*remember_data.*",
    category=FutureWarning,
    module=r"sktime\.forecasting\.base\._base"
)
warnings.filterwarnings(
    "ignore",
    message=r"`sklearn\.utils\.parallel\.delayed` should be used",
    category=UserWarning,
    module=r"sklearn\.utils\.parallel",
)


### Load the training panel and identify the economic predictors

train = pd.read_csv("data/processed/train.csv")
train["Period"] = pd.to_datetime(train["Period"])

exog_columns = config.ECONOMIC_FEATURES



for country, country_data in train.groupby("Country"):

    ### [A] Prepare the country's data

    country_data = (
        country_data
        .sort_values("Period")
        .set_index("Period")
        .asfreq("MS")
    )

    # Feature selection must see the full training panel.
    selection_data = country_data.reset_index()

    # Apply the usual publication cutoff for final model fitting.
    if config.APPLY_TRAINING_CUTOFF:
        fitting_data = country_data.iloc[
            :-config.IMMIGRATION_LAG
        ].copy()
    else:
        fitting_data = country_data.copy()

    y_train = fitting_data["Immigration"].astype(float)

    ### [B] Fit and save the baseline (unchanged)

    model = baseline.train_baseline(y_train)

    model_path = f"models/baseline_{country}.pkl"
    joblib.dump(model, model_path)

    logger.info(
        "Fitted baseline model for %s", country
    )

    ### [C] Select economic features for AR-X

    if config.FEATURE_SELECTION == "forward":
        arx_selected, arx_history = select_features(
            country=country,
            model_name="arx_fourier",
            country_data=selection_data,
            candidates=config.ECONOMIC_FEATURES,
        )

    elif config.FEATURE_SELECTION == "none":
        arx_selected = list(config.ECONOMIC_FEATURES)
        arx_history = []

    else:
        raise ValueError(
            f"Unknown feature selection mode: {config.FEATURE_SELECTION}"
        )

    # Use the same historical-imputation policy as validation.
    selection_split = len(country_data) - VALIDATION_MONTHS

    arx_X = prepare_features(
        country_data,
        arx_selected,
        selection_split,
    ).loc[fitting_data.index]

    # Scale selected predictors, if any.
    arx_scaler = None

    if arx_selected:

        arx_scaler = StandardScaler()

        arx_X_scaled = pd.DataFrame(
            arx_scaler.fit_transform(arx_X),
            index=arx_X.index,
            columns=arx_selected,
        )

    else:
        arx_X_scaled = None

    ### [D] Fit and save the selected AR-X model

    arx_model = arx_fourier.train_arx_fourier(
        y_train,
        arx_X_scaled,
        lags=config.ARX_LAGS,
        fourier_order=config.ARX_FOURIER_ORDER,
    )

    arx_artifact = {
        "model": arx_model,
        "scaler": arx_scaler,
        "exog_columns": arx_selected,
        "selection_history": arx_history,
    }

    model_path = f"models/arx_fourier_{country}.pkl"
    joblib.dump(arx_artifact, model_path)

    logger.info(
        "%s | AR-X selected: %s",
        country,
        arx_selected,
    )

    ### [E] Select economic features for Random Forest

    if config.FEATURE_SELECTION == "forward":
        rf_selected, rf_history = select_features(
            country=country,
            model_name="random_forest",
            country_data=selection_data,
            candidates=config.ECONOMIC_FEATURES,
        )

    elif config.FEATURE_SELECTION == "none":
        rf_selected = list(config.ECONOMIC_FEATURES)
        rf_history = []

    else:
        raise ValueError(
            f"Unknown feature selection mode: {config.FEATURE_SELECTION}"
        )

    rf_X = prepare_features(
        country_data,
        rf_selected,
        selection_split,
    ).loc[fitting_data.index]

    ### [F] Fit and save the selected Random Forest model

    rf_features = random_forest.make_features(
        y_train,
        rf_X,
    )

    first_row = max(config.RF_LAGS)

    rf_X_train = rf_features.iloc[first_row:]
    rf_y_train = y_train.iloc[first_row:]

    rf_model = random_forest.train_random_forest(
        rf_y_train,
        rf_X_train,
    )

    rf_artifact = {
        "model": rf_model,
        "scaler": None,
        "exog_columns": rf_selected,
        "selection_history": rf_history,
    }

    model_path = f"models/random_forest_{country}.pkl"
    joblib.dump(rf_artifact, model_path)

    logger.info(
        "%s | Random Forest selected: %s",
        country,
        rf_selected,
    )
