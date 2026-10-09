# src/config.py
"""Configuration settings for the complete forecasting pipeline."""


### Forecasting Horizons
FORECASTING_HORIZONS = [1, 3, 6]

### Baseline configuration
LAGS = 18
HOLDOUT_SIZE = 6

### AutoREG settings
TREND = "c"

