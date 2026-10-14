### src/models/baseline.py
"""Run the baseline AutoREG model for time series forecasting."""

from sktime.forecasting.auto_reg import AutoREG

from .. import config


def train_baseline(y_train):

    model = AutoREG(
        lags=config.LAGS,
        trend=config.TREND)

    model.set_config(remember_data=False)
    model.fit(y_train)

    return model
