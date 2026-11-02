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

import pandas as pd

from .utils import build_logger

logger = build_logger()


### Download the assembled data from GitHub and save in raw/ before preprocessing

url = "https://raw.githubusercontent.com/ben-mikus/nl-immigration-data/main/data/panel_data.csv"

logger.info("Downloading raw data from GitHub")
data = pd.read_csv(url)

os.makedirs("data/raw", exist_ok=True)
data.to_csv("data/raw/data.csv", index=False)
logger.info("Saved (%d rows) to data/raw/data.csv", len(data))


### Represent each observation as a calendar month rather than a specific day

data["Period"] = pd.PeriodIndex(
    pd.to_datetime(data["Period"].astype(str), format="%Y%m"),
    freq="M"
)


### Write the processed data to the processed/ directory, note that monthly periods will serialize as text

os.makedirs("data/processed", exist_ok=True)
data.to_csv("data/processed/data.csv", index=False)
logger.info("Saved processed data to data/processed/data.csv")
