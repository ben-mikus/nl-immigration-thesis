### src/models/baseline.py
"""
src.models.baseline defines the autoregression model used as the immigration-only baseline forecaster. The baseline
serves as a simple benchmark against which more complex models can be compared.
"""


from sktime.forecasting.auto_reg import AutoREG

from .. import config


def train_baseline(y_train):
    """Fit an autoregessive baseline to an immigration time series.
    
    Parameters
    ----------
    y_train : pd.Series
        The training time series of immigration counts.

    Returns
    -------
    model : sktime.forecasting.auto_reg.AutoREG
        The fitted autoregressive baseline model.

    Notes
    -----
    The lag specification and deterministic trend values are pre-specified in the . config module. The estimator is con-
    figured with a remember_data flag set to False to disable sktime's retention of input data. Model fitting and fore-
    casting are handled by the underlying AutoREG implementation.

    This function is called for fitting a baseline model in both src.train and src.predict.
    """


    model = AutoREG(
        lags=config.BASELINE_LAGS,
        trend=config.BASELINE_TREND)

    model.set_config(remember_data=False)
    model.fit(y_train)

    return model
