# src/train.py
"""Train and save the forecasting models."""


import os
import warnings
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .models import baseline, dynamic, auto_fourier
from .utils import build_logger

logger = build_logger()

warnings.filterwarnings(
    "ignore",
    message=r"The default of config .*remember_data.*",
    category=FutureWarning,
    module=r"sktime\.forecasting\.base\._base"
)


### Load the training set

train = pd.read_csv("data/processed/train.csv")
train["Period"] = pd.to_datetime(train["Period"])

exog_columns = [
    column
    for column in train.columns
    if column not in ["Country", "Period", "Immigration"]
]


### Train a spearate model for each country

os.makedirs("models", exist_ok=True)

for country, country_data in train.groupby("Country"):

    ### Prepare a shared monthly index for target and predictors:

    country_data = (
        country_data
        .sort_values("Period")
        .set_index("Period")
        .asfreq("MS")
    )

    y_train = country_data["Immigration"]
    X_train = country_data[exog_columns]


    ### Fit and save the AutoREG baseline for each country

    model = baseline.train_baseline(y_train)

    model_path = f"models/baseline_{country}.pkl"
    joblib.dump(model, model_path)
    logger.info(f"Fitted baseline AutoREG model for {country} saved to {model_path}")


    ### Scale predictors using this country's training data

    X_train = X_train.apply(pd.to_numeric, errors="raise")

    scaler = StandardScaler()

    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        index=X_train.index,
        columns=X_train.columns,
    )

    # ### Fit and save dynamic model with its preprocessing information

    # model = dynamic.train_dynamic(y_train, X_train_scaled)
    
    # artifact = {
    #     "model": model,
    #     "scaler": scaler,
    #     "exog_columns": exog_columns,
    # }

    # model_path = f"models/dynamic_{country}.pkl"
    # joblib.dump(artifact, model_path)

    # logger.info(
    #     "Saved Dynamic Regression model for %s to %s",
    #     country,
    #     model_path,
    # )

    ### Fit and save ARX with Fourier terms for each country

    model = auto_fourier.train_arx_fourier(
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
