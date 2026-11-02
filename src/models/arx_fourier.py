### src/models/arx_fourier.py
"""
src.models.arx_fourier defines the "Dynamic Harmonic Regression" model; an AutoRegressive model with Fourier seasonality
and exogenous predictors. The model extends immigration-only autoregression by incorporating economic predictors as well
as Fourier terms to represent annual seasonality.
"""


from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.deterministic import DeterministicProcess


def train_arx_fourier(y_train, X_train, lags=2, fourier_order=3):
    """Fit an AutoRegressive model with Fourier seasonality and exogenous predictors.
    
    Parameters
    ----------
    y_train : pd.Series
        The training time series of immigration counts.
    X_train : pd.DataFrame
        The exogenous predictors for the training period.
    lags : int, optional
        The number of autoregressive lags to include, by default 2.
    fourier_order : int, optional
        The order of the Fourier terms for seasonality, by default 3.

    Returns
    -------
    model : statsmodels.tsa.ar_model.AutoRegResults
        The fitted AutoRegressive model with Fourier seasonality and exogenous predictors.
    
    Notes
    -----
    AutoReg's separate trend is disabled because of the inclusion of the deterministic Fourier seasonality terms. Any
    missing values raise an error. Any scaling is the user's responsibility and does not take place within the function.

    This function is called for fitting a DHR model in both src.train and src.predict.
    """

    ### Define the annual seasonality on the training index using Fourier terms

    seasonality = DeterministicProcess(
        index=y_train.index,
        constant=True,
        period=12,
        fourier=fourier_order,
    )


    ### Combine immigration lags, economic predictors, and deterministic terms

    model = AutoReg(
        y_train,
        lags=lags,
        exog=X_train,
        deterministic=seasonality,
        trend="n",
        missing="raise",
    )

    return model.fit()
