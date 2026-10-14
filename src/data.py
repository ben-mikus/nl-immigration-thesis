### src/data.py
"""
Ingests and preprocess the immigration data.

Current: Simply converts the "Period" column to a pandas PeriodIndex

Planned: Handle missing values and multiple countries
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


### Load the data from GitHub and save in raw/ before preprocessing

url = "https://raw.githubusercontent.com/ben-mikus/nl-immigration-data/main/data/panel_data.csv"

logger.info("Downloading raw data from GitHub")
data = pd.read_csv(url)

Path("data/raw").mkdir(parents=True, exist_ok=True)
data.to_csv("data/raw/data.csv", index=False)
logger.info("Saved (%d rows) to data/raw/data.csv", len(data))


### Preprocess the data and save in processed/

logger.info("Preprocessing data")
data["Period"] = pd.PeriodIndex(
    pd.to_datetime(data["Period"].astype(str), format="%Y%m"),
    freq="M"
)

Path("data/processed").mkdir(parents=True, exist_ok=True)
data.to_csv("data/processed/data.csv", index=False)
logger.info("Saved processed data to data/processed/data.csv")
