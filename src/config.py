# src/config.py
"""Configuration settings for the complete forecasting pipeline."""


### General configuration

FORECASTING_HORIZONS = [1, 3, 6]
TEST_SIZE = 60


### AutoREG configuration

BASELINE_LAGS = 18
BASELINE_TREND = "c"


# ### SARIMAX configuration

# SARIMAX_ORDER = (2, 0, 0)
# SARIMAX_SEASONAL_ORDER = (1, 0, 0, 12)
# SARIMAX_TREND = "c"

# EXOG_FORECAST_STRATEGY = "carry_forward"


### Random Forest configuration

RF_LAGS = (1, 2)
RF_FOURIER_ORDER = 3

RF_N_ESTIMATORS = 200
RF_MIN_SAMPLES_LEAF = 3
RF_MAX_FEATURES = 0.8

RF_RANDOM_STATE = 42
RF_N_JOBS = -1