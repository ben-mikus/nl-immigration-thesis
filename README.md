# Forecasting Intra-EU Migration to the Netherlands


Demographic change, including migration, has important implications for the planning of Dutch housing, infrastructure, and public services. Anticipating short-term migration flows can therefore keep policymakers and business owners informed and support broader planning. This project aims to support said motivation by forecasting total monthly immigration from selected European Union (EU) countries to the Netherlands using migration history and macroeconomic conditions.

## Methodology

The pipeline downloads a monthly migration dataset, reserves the latest six
months as a holdout set, and fits an autoregressive baseline model to the
remaining observations. It produces forecasts and reports mean absolute error
(MAE) at one-, three-, and six-month horizons.

The current baseline uses Polish immigration data and an AutoREG model. The
planned work will compare statistical and machine-learning models, add selected
origin- and destination-country economic indicators, and examine results across
Dutch business-cycle conditions. See [reports/](reports/) for the literature
review and the planned methodology documentation.

## Project Status

The baseline pipeline is complete: it downloads data, creates a train/holdout
split, trains an AutoREG model, and writes evaluation metrics. The supplied
dataset covers monthly Polish immigration from January 2010 through December
2025.

The broader implementation is in progress. Additional countries, multivariate
features, model comparisons, business-cycle analysis, tests, and the Streamlit
deployment are planned but not yet implemented.

## Repository Structure

```text
u142701-capstone
├── data/                 Downloaded and generated datasets
│   ├── raw/              Downloaded source CSV files
│   ├── processed/        Prepared data plus train/holdout splits
│   └── README.md         Dataset coverage, sources, and limitations
├── deployment/           Planned Streamlit application
├── keys/                 
├── logs/                 Pipeline logs
├── models/               Trained model artifacts
├── notebooks/            Exploratory analysis notebooks
├── reports/              Literature review and planned methodology reports
├── results/              Forecast evaluation outputs
├── scripts/              Supporting shell scripts
├── src/                  Forecasting pipeline source code
│   ├── config.py         Forecast horizons and baseline model settings
│   ├── data.py           Downloads and prepares the source dataset
│   ├── split.py          Creates training and holdout time-series splits
│   ├── train.py          Fits and saves the forecasting model
│   ├── predict.py        Generates forecasts and calculates MAE metrics
│   ├── utils.py          Shared logging utilities
│   └── models/
│       └── baseline.py   Defines the AutoREG baseline model
├── tests/                Automated tests (planned)
├── Makefile              Pipeline and cleanup commands
└── requirements.txt      Pinned Python dependencies
```

## How to run

Begin by cloning the repository to your machine:

```bash
git clone https://gitlab.uvt.nl/u1427011/u142701-capstone.git u142701
cd u142701
```

If you are viewing this repository from GitHub, clone with:

```bash
git clone https://github.com/ben-mikus/nl-immigration-thesis.git u142701
cd u142701
```

On a new Ubuntu or WSL installation, install the required tools:

```bash
sudo apt update
sudo apt install -y git make python3 python3-venv python3-pip
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the pinned project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Then, the complete pipeline can reproduced form the repositoy root with:

```bash
make all
```

`make all` downloads the source dataset, creates the train/holdout split,
trains the baseline model, and writes metrics to `results/metrics.csv`.

## Available Commands

The `Makefile` provides shortcuts for common tasks, many of which make up `make all`. Run these from Ubuntu/WSL with the virtual environment activated to explore different parts of the pipeline. Run `make help` to view this table in your terminal.

| Command | Description |
| --- | --- |
| `make all` | Remove generated data and outputs, then run the full pipeline. |
| `make data` | Download and preprocess the source dataset. |
| `make split` | Create training and holdout datasets from processed data. |
| `make train` | Train and save the baseline AutoREG model. |
| `make predict` | Generate holdout forecasts and write MAE metrics. |
| `make clear-data` | Remove downloaded raw and processed CSV files. |
| `make clear-cache` | Remove model, log, and result files. |
| `make clear-all` | Remove both generated data and cached outputs. |
| `make help` | Show the available Make targets. |
