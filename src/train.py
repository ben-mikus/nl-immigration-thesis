### src/train.py
"""
src.train fits and saves forecasting models for each country-model combination. This module consumes the training panel
produced by src.split and fits an autoregressive baseline, an AR-X model with Fourier seasonality, and a Random Forest 
regressor model for each country. The saved .pkl artifacts represent models fitted to the original training panel and do
not feed into src.predict for walk-forward evaluation.

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


import os
import warnings

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from . import config
from .models import baseline, dhr, random_forest
from .utils import build_logger

logger = build_logger()

warnings.filterwarnings(
    "ignore",
    message=r"The default of config .*remember_data.*",
    category=FutureWarning,
    module=r"sktime\.forecasting\.base\._base"
)


### Load the training panel and identify the economic predictors

train = pd.read_csv("data/processed/train.csv")
train["Period"] = pd.to_datetime(train["Period"])

exog_columns = [
    column
    for column in train.columns
    if column not in ["Country", "Period", "Immigration"]
]


### Loop through each country to fit a separate model on each country's training sample

os.makedirs("models", exist_ok=True)

for country, country_data in train.groupby("Country"):

    ### [A] Prepare the country's data and align it to a monthly time index

    country_data = (
        country_data
        .sort_values("Period")
        .set_index("Period")
        .asfreq("MS")
    )

    y_train = country_data["Immigration"]
    X_train = country_data[exog_columns]


    ### [B] Fit and save the AutoREG baseline for each country

    model = baseline.train_baseline(y_train)

    model_path = f"models/baseline_{country}.pkl"
    joblib.dump(model, model_path)
    logger.info(f"Fitted baseline AutoREG model for {country} saved to {model_path}")


    ### [C] Scale predictors using this country's training data

    X_train = X_train.apply(pd.to_numeric, errors="raise")

    scaler = StandardScaler()

    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        index=X_train.index,
        columns=X_train.columns,
    )


    ### [C] Fit and save ARX with Fourier terms for each country

    model = dhr.train_arx_fourier(
        y_train,
        X_train_scaled,
        lags=2,
        fourier_order=3,
    )

    artifact = {
        "model": model,
        "scaler": scaler,
        "exog_columns": exog_columns,
    }

    model_path = f"models/arx_fourier_{country}.pkl"
    joblib.dump(artifact, model_path)
    logger.info(f"Fitted ARX with Fourier terms model for {country} saved to {model_path}")


    ### [D] Fit and save Random Forest model for each country

    rf_features = random_forest.make_features(y_train, X_train)

    first_row = max(config.RF_LAGS)

    rf_X_train = rf_features.iloc[first_row:]
    rf_y_train = y_train.iloc[first_row:]

    rf_model = random_forest.train_random_forest(
        rf_y_train,
        rf_X_train,
    )

    artifact = {
        "model": rf_model,
        "scaler": scaler,
        "exog_columns": exog_columns,
    }

    model_path = f"models/random_forest_{country}.pkl"
    joblib.dump(artifact, model_path)
    logger.info(f"Fitted Random Forest model for {country} saved to {model_path}")
