### src/models/dynamic.py
"""Dynamic regresssion with annual Fourier seasonality and AR(2) errors."""

"""Dynamic regression with annual Fourier seasonality and AR(2) errors."""

import pandas as pd
from statsmodels.tsa.deterministic import DeterministicProcess
from statsmodels.tsa.statespace.sarimax import SARIMAX


def train_dynamic(y_train, X_train, fourier_order=3):
    """Fit the model and return its seasonal-term generator."""

    seasonality = DeterministicProcess(
        index=y_train.index,
        period=12,
        fourier=fourier_order,
    )

    fourier_train = seasonality.in_sample()

    predictors = pd.concat(
        [X_train, fourier_train],
        axis=1,
    )

    model = SARIMAX(
        y_train,
        exog=predictors,
        order=(2, 0, 0),
        seasonal_order=(0, 0, 0, 0),
        trend="c",
    )

    fitted_model = model.fit(disp=False, maxiter=200)

    return fitted_model, seasonality