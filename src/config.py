# src/config.py
"""Configuration settings for the complete forecasting pipeline."""

### Economic features used as predictors in the models

ECONOMIC_FEATURES = [
    "NL-CONJCLK",
]


### PUBLICATION LAGS specifies the number of months to shift forward by release frequency
PUBLICATION_LAGS = {
    "monthly": 2,
    "quarterly": 4,
    "semiannual": 8,
}

### IMMIGRATION_LAG specifies the number of months to shift forward for immigration observations
IMMIGRATION_LAG = 1
APPLY_TRAINING_CUTOFF = True

### General configuration

FORECASTING_HORIZONS = [1, 3, 6]
TEST_SIZE = 60


### AutoREG configuration

BASELINE_LAGS = 18
BASELINE_TREND = "c"


### Random Forest configuration

RF_LAGS = (1, 2)
RF_FOURIER_ORDER = 3

RF_N_ESTIMATORS = 200
RF_MIN_SAMPLES_LEAF = 3
RF_MAX_FEATURES = 0.8

RF_RANDOM_STATE = 42
RF_N_JOBS = -1