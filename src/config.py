# src/config.py
"""Configuration settings for the complete forecasting pipeline."""


### Countries included in the analysis

COUNTRIES = [
    "Bulgaria",
    "Germany",
    "Italy",
    "Poland",
    "Romania",
    "Spain"
]


### Economic features used as predictors in the models

ECONOMIC_FEATURES = [
    "NL-CONJCLK",
    # "Country-MINWAGE",
    # "NL-MINWAGE",
    "MINWAGE-RATIO",
    # "Country-WAGESAL",
    # "NL-WAGESAL",
    # "WAGESAL-GROWTH",
    # "NL-WAGESAL-GROWTH",
    "WAGESAL-GAP",
    # "Country-UNEMP",
    # "NL-UNEMP",
    "UNEMP-GAP",
    "UNEMP-CHANGE",
    "NL-UNEMP-CHANGE",
    # "Country-GDP",
    # "NL-GDP",
    "GDP-GROWTH-GAP"
]

CHANGE_IN_MONTHS = 12  # Number of periods to use for percentage change calculations


FEATURE_SELECTION = "forward"  # "none" or "forward"

MAX_SELECTED_FEATURES = 3

MIN_MAE_IMPROVEMENT = 1.0


### PUBLICATION LAGS specifies the number of months to shift forward by release frequency
PUBLICATION_LAGS = {
    "monthly": 2,
    "quarterly": 5,
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

### AR-X Configuration

ARX_LAGS = [1, 2, 12]
ARX_TREND = "c"
ARX_FOURIER_ORDER = 3

### Random Forest configuration

RF_LAGS = (1, 2)
RF_FOURIER_ORDER = 3

RF_N_ESTIMATORS = 50
RF_MIN_SAMPLES_LEAF = 1
RF_MAX_FEATURES = 0.8

RF_RANDOM_STATE = 42
RF_N_JOBS = -1