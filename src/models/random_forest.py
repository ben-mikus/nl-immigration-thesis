### src/models/random_forest.py
"""Random Forest regression model."""

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from .. import config


def train_random_forest(y_train, X_train):
    """Fit using an already prepared feature matrix."""

    model = RandomForestRegressor(
        n_estimators=config.RF_N_ESTIMATORS,
        min_samples_leaf=config.RF_MIN_SAMPLES_LEAF,
        max_features=config.RF_MAX_FEATURES,
        random_state=config.RF_RANDOM_STATE,
        n_jobs=config.RF_N_JOBS,
    )

    model.fit(X_train, y_train)

    return model


def make_features(y, X):
    """Combine economics, previous immigration, and annual seasonality."""

    features = X.astype(float).add_prefix("economic__")

    for lag in config.RF_LAGS:
        features[f"immigration_lag_{lag}"] = (
            y.shift(lag).reindex(X.index)
        )

    month = X.index.month.to_numpy() - 1

    for k in range(1, config.RF_FOURIER_ORDER + 1):
        angle = 2 * np.pi * k * month / 12
        features[f"fourier_sin_{k}"] = np.sin(angle)
        features[f"fourier_cos_{k}"] = np.cos(angle)

    return features