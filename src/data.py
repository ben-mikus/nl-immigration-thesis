### src/data.py
"""
src.data provides the local data input for the forecasting pipeline. It retrieves a pre-assembled panel dataset from
a separate GitHub repository, saves a copy before transformation, then standardizes the dataset and applies publication
lags to economic indicators. The processed dataset is consumed by src.split.

Workflow
-----
1. Download the CSV into a Pandas DataFrame.
2. Save the raw data to data/raw/data.csv.
3. Standardize the Period column and filter countries.
4. Validate economic indicators and apply publication lags based on reporting frequency.
5. Remove observations missing essential fields and save the processed data to data/processed/data.csv.

Notes
-----
This module validates required columns and reports missing economic values, but does not explicitly check for duplicate
observations, missing monthly periods, or other data quality issues. It is assumed that the input data from GitHub is
otherwise clean and well-structured. Publication lags approximate the availability of economic indicators to prevent
look-ahead bias. For more details on the data source and its structure, refer to data/README.md.

Run from the repository root through ``python3 -m src.data`` or ``make data``. Output directories are created as needed
and existing CSVs are overwritten.
"""


import os

import numpy as np
import pandas as pd

from . import config
from .utils import build_logger

logger = build_logger()


### Publication frequencies for original economic indicators

FEATURE_FREQUENCIES = {
    "NL-CONJCLK": "monthly",
    "Country-MINWAGE": "semiannual",
    "NL-MINWAGE": "semiannual",
    "MINWAGE-RATIO": "semiannual",
    "Country-WAGESAL": "quarterly",
    "NL-WAGESAL": "quarterly",
    "WAGESAL-GROWTH": "quarterly",
    "NL-WAGESAL-GROWTH": "quarterly",
    "WAGESAL-GAP": "quarterly",
    "Country-UNEMP": "monthly",
    "NL-UNEMP": "monthly",
    "UNEMP-GAP": "monthly",
    "UNEMP-CHANGE": "monthly",
    "NL-UNEMP-CHANGE": "monthly",
    "Country-GDP": "quarterly",
    "NL-GDP": "quarterly",
    "GDP-GROWTH-GAP": "quarterly"
}


### Download the assembled data from GitHub and save the untouched raw input

url = "https://raw.githubusercontent.com/ben-mikus/nl-immigration-data/main/data/panel_data.csv"

logger.info("Downloading raw data from GitHub")
data = pd.read_csv(url)

os.makedirs("data/raw", exist_ok=True)
data.to_csv("data/raw/data.csv", index=False)
logger.info("Saved %d rows to data/raw/data.csv", len(data))


### Standardize the monthly period and filter countries

required_columns = {"Period", "Country", "Immigration"}
missing_required = required_columns - set(data.columns)
if missing_required:
    raise ValueError(f"Missing required input columns: {sorted(missing_required)}")

data["Period"] = pd.PeriodIndex(
    pd.to_datetime(data["Period"].astype(str), format="%Y%m"),
    freq="M",
)

if config.COUNTRIES is not None:
    data = data[data["Country"].isin(config.COUNTRIES)].copy()
    if data.empty:
        raise ValueError(f"No observations found for {config.COUNTRIES}")

data = data.sort_values(["Country", "Period"]).copy()
logger.info("Selected countries: %s", sorted(data["Country"].unique()))


### Retain only the configured economic features

required_features = set(config.ECONOMIC_FEATURES)
missing_features = required_features - set(data.columns)

if missing_features:
    raise ValueError(
        f"Configured economic features missing from source: "
        f"{sorted(missing_features)}"
    )

data = data[
    ["Period", "Country", "Immigration"]
    + config.ECONOMIC_FEATURES
].copy()

logger.info(
    "Retained %d configured economic features",
    len(config.ECONOMIC_FEATURES),
)


### Validate source indicators and apply publication delays

unconfigured_features = (
    set(data.columns) - required_columns - set(FEATURE_FREQUENCIES)
)
if unconfigured_features:
    raise ValueError(
        "Economic indicators missing publication-lag configuration: "
        f"{sorted(unconfigured_features)}"
    )

for feature, frequency in FEATURE_FREQUENCIES.items():
    if feature not in data.columns:
        continue

    data[feature] = pd.to_numeric(data[feature], errors="raise")
    lag = config.PUBLICATION_LAGS[frequency]
    data[feature] = data.groupby("Country")[feature].shift(lag)
    logger.info("Applied %d-month publication lag to %s", lag, feature)


### Drop only observations missing essential forecasting fields

rows_before = len(data)
data = data.dropna(subset=["Period", "Country", "Immigration"])
logger.info(
    "Removed %d rows with missing essential fields; retained missing economic values",
    rows_before - len(data),
)

### Visibility into missing candidate data without removing any further rows.

for country, group in data.groupby("Country"):
    missing_counts = group[config.ECONOMIC_FEATURES].isna().sum()
    incomplete = {k: int(v) for k, v in missing_counts.items() if v > 0}
    if incomplete:
        logger.info("%s | Missing candidate values: %s", country, incomplete)


### Write the processed panel

os.makedirs("data/processed", exist_ok=True)
data.to_csv("data/processed/data.csv", index=False)
logger.info("Saved processed data (%d rows) to data/processed/data.csv", len(data))
