### src/models/sarimax.py
"""Store the SARIMAX model for time series forecasting."""

from sktime.forecasting.sarimax import SARIMAX

from .. import config


def train_sarimax(y_train, X_train, start_params=None):
    """Train a SARIMAX model using the provided training data."""

    model = SARIMAX(
        order=config.SARIMAX_ORDER,
        seasonal_order=config.SARIMAX_SEASONAL_ORDER,
        trend=config.SARIMAX_TREND,
        maxiter=200,
        start_params=start_params
    )

    model.set_config(remember_data=False)
    model.fit(y_train, X=X_train)

    return model