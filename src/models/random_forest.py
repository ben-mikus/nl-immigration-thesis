### src/models/random_forest.py
"""
src.models.random_forest constructs forecasting features and defines the Random Forest regression model.

The Random Forest model predicts immigration from lagged immigration values, economic features, and annual seasonality.
Its tree-based structure allows nonlinear interactions among variables to be captured without explicit specification.
"""


import numpy as np
from sklearn.ensemble import RandomForestRegressor

from .. import config


def make_features(y, X):
    """Build features from economic indicators, previous immigration, and annual seasonality.

    Parameters
    ----------
    y : pd.Series
        The time series of immigration counts.
    X : pd.DataFrame
        The exogenous predictors for the corresponding period.

    Returns
    -------
    features : pd.DataFrame
        The constructed feature matrix including economic indicators, lagged immigration, and Fourier terms.
    
    Notes
    -----
    Lagging shifts observations by row position and interpreting these shifts as monthly lags assumes a complete and
    ordered monthly series. The lag specification and Fourier order values are pre-specified in the . config module.
    """


    ### Convert economic predictors to float and add prefix their names

    features = X.astype(float).add_prefix("economic__")


    ### Shift immigration by each configured lag and align it to X.index

    for lag in config.RF_LAGS:
        features[f"immigration_lag_{lag}"] = (
            y.shift(lag).reindex(X.index)
        )


    ### Derive annual Fourier terms from each row's calendar month

    month = X.index.month.to_numpy() - 1

    for k in range(1, config.RF_FOURIER_ORDER + 1):
        angle = 2 * np.pi * k * month / 12
        features[f"fourier_sin_{k}"] = np.sin(angle)
        features[f"fourier_cos_{k}"] = np.cos(angle)


    return features


def train_random_forest(y_train, X_train):
    """Fit a Random Forest Regressor to an already prepared feature matrix.
    
    Parameters
    ----------
    y_train : pd.Series
        The training time series of immigration counts.
    X_train : pd.DataFrame
        The exogenous predictors for the corresponding period.

    Returns
    -------
    model : sklearn.ensemble.RandomForestRegressor
        The fitted Random Forest regression model.

    Notes
    -----
    The Random Forest is configured with pre-specified hyperparameters in the . config module. The random seed controls
    the reproducibility of the model fitting process, and n_jobs controls parallel computation.    
    """


    model = RandomForestRegressor(
        n_estimators=config.RF_N_ESTIMATORS,
        min_samples_leaf=config.RF_MIN_SAMPLES_LEAF,
        max_features=config.RF_MAX_FEATURES,
        random_state=config.RF_RANDOM_STATE,
        n_jobs=config.RF_N_JOBS,
    )

    model.fit(X_train, y_train)

    return model
