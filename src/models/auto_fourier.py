"""Autoregressive regression with economic predictors and Fourier seasonality."""

from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.deterministic import DeterministicProcess


def train_arx_fourier(y_train, X_train, lags=2, fourier_order=3):
    """Fit by ordinary least squares, without iterative optimization."""

    seasonality = DeterministicProcess(
        index=y_train.index,
        constant=True,
        period=12,
        fourier=fourier_order,
    )

    model = AutoReg(
        y_train,
        lags=lags,
        exog=X_train,
        deterministic=seasonality,
        trend="n",
        missing="raise",
    )

    return model.fit()