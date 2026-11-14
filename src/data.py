### src/data.py
"""
src.data provides the local data input for the forecasting pipeline. It retrieves a pre-assembled panel dataset from
a separate GitHub repository, saves a copy before transformation, then standardizes the dataset. The standardized data-
set is consumed by src.split.

Workflow
-----
1. Download the CSV into a Pandas DataFrame.
2. Save the raw data to data/raw/data.csv.
3. Preprocess the data (standardize the Period column).
4. Save the processed data to data/processed/data.csv.

Notes
-----
This module does not explicitly validate the panel schema, check for duplicate or missing values, or handle other data 
quality issues. It is assumed that the input data from GitHub is already clean and well-structured. For more details on
the data source and its structure, refer to data/README.md.

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
    "Country-WAGESAL": "quarterly",
    "NL-WAGESAL": "quarterly",
    "Country-UNEMP": "monthly",
    "NL-UNEMP": "monthly",
    "Country-JOBVAC": "quarterly",
    "NL-JOBVAC": "quarterly",
    "Country-HICP": "monthly",
    "NL-HICP": "monthly",
    "Country-GDP": "quarterly",
    "NL-GDP": "quarterly",
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
        # An unavailable indicator remains an eligible *candidate column*,
        # but feature selection will have to exclude it for this country.
        data[feature] = np.nan
        logger.warning("Missing %s; retaining as an empty candidate column", feature)
        continue

    data[feature] = pd.to_numeric(data[feature], errors="raise")
    lag = config.PUBLICATION_LAGS[frequency]
    data[feature] = data.groupby("Country")[feature].shift(lag)
    logger.info("Applied %d-month publication lag to %s", lag, feature)


### Engineer economic features from publication-adjusted inputs

# Relative labour-market indicators

data["UNEMP-GAP"] = data["Country-UNEMP"] - data["NL-UNEMP"]
data["JOBVAC-GAP"] = data["NL-JOBVAC"] - data["Country-JOBVAC"]

# Changes in unemployment (percentage points), over configured months

data["UNEMP-CHANGE"] = (
    data.groupby("Country")["Country-UNEMP"].diff(config.CHANGE_IN_MONTHS)
)
data["NL-UNEMP-CHANGE"] = (
    data.groupby("Country")["NL-UNEMP"].diff(config.CHANGE_IN_MONTHS)
)

# Wage growth over configured months

data["WAGESAL-GROWTH"] = (
    data.groupby("Country")["Country-WAGESAL"]
    .pct_change(config.CHANGE_IN_MONTHS, fill_method=None) * 100
)
data["NL-WAGESAL-GROWTH"] = (
    data.groupby("Country")["NL-WAGESAL"]
    .pct_change(config.CHANGE_IN_MONTHS, fill_method=None) * 100
)

# Inflation rates and inflation gap over configured months

data["Country-INFLATION"] = (
    data.groupby("Country")["Country-HICP"]
    .pct_change(config.CHANGE_IN_MONTHS, fill_method=None) * 100
)
data["NL-INFLATION"] = (
    data.groupby("Country")["NL-HICP"]
    .pct_change(config.CHANGE_IN_MONTHS, fill_method=None) * 100
)
data["HICP-GAP"] = data["Country-INFLATION"] - data["NL-INFLATION"]

# Relative minimum wages; missing where no national minimum wage exists

data["MINWAGE-RATIO"] = (
    data["NL-MINWAGE"] / data["Country-MINWAGE"].replace(0, np.nan)
)

# GDP growth and relative growth over configured months

data["Country-GDP-GROWTH"] = (
    data.groupby("Country")["Country-GDP"]
    .pct_change(config.CHANGE_IN_MONTHS, fill_method=None) * 100
)
data["NL-GDP-GROWTH"] = (
    data.groupby("Country")["NL-GDP"]
    .pct_change(config.CHANGE_IN_MONTHS, fill_method=None) * 100
)
data["GDP-GROWTH-GAP"] = (
    data["NL-GDP-GROWTH"] - data["Country-GDP-GROWTH"]
)

# Replace undefined percentage changes with missing values, not infinity.
data = data.replace([np.inf, -np.inf], np.nan)


### Drop only observations missing essential forecasting fields

rows_before = len(data)
data = data.dropna(subset=["Period", "Country", "Immigration"])
logger.info(
    "Removed %d rows with missing essential fields; retained missing economic values",
    rows_before - len(data),
)

# Visibility into missing candidate data without removing any further rows.
for country, group in data.groupby("Country"):
    missing_counts = group[config.ECONOMIC_FEATURES].isna().sum()
    incomplete = {k: int(v) for k, v in missing_counts.items() if v > 0}
    if incomplete:
        logger.info("%s | Missing candidate values: %s", country, incomplete)


### Write the processed panel

os.makedirs("data/processed", exist_ok=True)
data.to_csv("data/processed/data.csv", index=False)
logger.info("Saved processed data (%d rows) to data/processed/data.csv", len(data))
