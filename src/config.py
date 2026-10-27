# src/config.py
"""Configuration settings for the complete forecasting pipeline."""


### General configuration

FORECASTING_HORIZONS = [1, 3, 6]
TEST_SIZE = 60


### AutoREG configuration

BASELINE_LAGS = 18
BASELINE_TREND = "c"


### SARIMAX configuration

SARIMAX_ORDER = (2, 0, 0)
SARIMAX_SEASONAL_ORDER = (1, 0, 0, 12)
SARIMAX_TREND = "c"

EXOG_FORECAST_STRATEGY = "carry_forward"