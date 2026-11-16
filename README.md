# Forecasting Intra-EU Migration to the Netherlands


Demographic change, including migration, has important implications for the planning of Dutch housing, infrastructure, and public services. Anticipating short-term migration flows can therefore keep policymakers and business owners informed and support broader planning. This master's thesis investigates the forecasting of monthly immigration to the Netherlands from six European Union (EU) countries: Bulgaria, Germany, Italy, Poland, Romania, and Spain. The project evaluates whether historical immigration patterns and macroeconomic indicators can be used to generate accurate short-term forecasts, comparing statistical and machine-learning approaches across one-, three-, and six-month forecasting horizons.

## Methodology

The project implements a reproducible forecasting pipeline that retrieves and preprocesses monthly immigration and macroeconomic data for six EU countries. Preprocessing includes accounting for economic indicator publication delays and splitting observations chronologically into training and testing datasets. Three forecasting approaches are compared: an autoregressive baseline (AutoREG) using historical immigration observations, an autoregressive model with Fourier seasonality (AR-X), and a Random Forest regression model. The latter two models support country-specific economic predictors selected through forward feature selection based on validation performance.

Forecasting accuracy is evaluated at 1-, 3-, and 6-month horizons using chronological walk-forward evaluation, in which models incorporate newly available observations without refitting their parameters. Performance is measured using Mean Absolute Error (MAE) and Weighted Absolute Percentage Error (WAPE), allowing comparisons across models, forecasting horizons, and countries. The analysis additionally investigates whether macroeconomic indicators improve predictive accuracy and how forecasting performance relates to Dutch economic conditions. For further details, refer to [reports/](reports/) for the literature
review, methodology, and technical report.

## Project Status

The principal forecasting pipeline has been implemented, including:
- Data retrieval and preprocessing.
- Publication-lag adjustments and economic feature engineering.
- Chronological training and testing splits.
- Training of all three forecasting models.
- Optional forward selection of economic predictors.
- Walk-forward forecasting without repeated model fitting.
- Calculation of MAE and WAPE.
- Country-specific forecast visualization and evaluation outputs.
The pipeline supports the six countries included in the study, with country selection and model specifications controlled through src/config.py.

The repository also contains academic documentation, including the literature review, methodology overview, ELSA report, and technical report.

Automated testing and the Streamlit deployment interface remain incomplete. The current deployment module is a placeholder rather than a functional forecasting application.

## Repository Structure

```text
u142701-capstone
├── data/
│   ├── raw/                  Downloaded source dataset
│   ├── processed/            Prepared data and train/test splits
│   └── README.md             Dataset documentation
├── deployment/
│   └── app.py                Streamlit application placeholder
├── notebooks/                Exploratory analysis artifacts
├── reports/                  Academic documentation
├── results/                  Forecasts, metrics, and visualizations
├── scripts/                  Supporting shell scripts
├── src/
│   ├── config.py             Pipeline and model configuration
│   ├── data.py               Downloads and prepares the source dataset
│   ├── split.py              Creates chronological train/test splits
│   ├── features.py           Economic predictor selection
│   ├── train.py              Fits and saves the forecasting models
│   ├── predict.py            Generates forecasts and calculates MAE metrics
│   ├── results.py            Displays metrics and creates horizon comparison charts
│   ├── utils.py              Shared logging utilities
│   └── models/
│       ├── baseline.py       Autoregressive baseline
│       ├── arx_fourier.py    AR-X with Fourier seasonality
│       └── random_forest.py  Random Forest regression
├── tests/                    Automated testing (planned)
├── Makefile                  Pipeline execution commands
└── requirements.txt          Python dependencies
```

Generated model artifacts and execution logs are stored locally in models/ and logs/, respectively.

## How to Run

The pipeline is designed to run in a Linux environment or through Windows Subsystem for Linux (WSL).

### 1. Clone the Repository

```bash
git clone https://gitlab.uvt.nl/u1427011/u142701-capstone.git u142701
cd u142701
```

If you are viewing this repository from GitHub, clone with:

```bash
git clone https://github.com/ben-mikus/nl-immigration-thesis.git u142701
cd u142701
```

### 2. Install System Requirements

On a new Ubuntu or WSL installation, install the required tools:

```bash
sudo apt update
sudo apt install -y git make python3 python3-venv python3-pip
```

### 3. Create and Activate the Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the pinned project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Execute the Pipeline

Run the complete workflow using:

```bash
make all
```

**Note:** Running `make all` removes all previously generated data, model artifacts, logs, and results before recreating them. Preserve any outputs needed for comparison before executing the command.

The project's `Makefile` additionally supports executing the core stages of the pipeline individually. Run these from Ubuntu/WSL with the virtual environment activated to explore different parts of the pipeline. When running stages individually, their preceding stages must already have produced the required inputs. Run `make help` to view this table in your terminal.

| Command | Description |
| --- | --- |
| `make all` | Remove generated data and outputs, then run the full pipeline. |
| `make data` | Download and preprocess the source dataset. |
| `make split` | Create training and holdout datasets from processed data. |
| `make train` | Train and save the baseline AutoREG model. |
| `make predict` | Generate holdout forecasts plus forecast and MAE tables. |
| `make results` | Display MAE metrics and create the horizon comparison chart. |
| `make clear-data` | Remove downloaded raw and processed CSV files. |
| `make clear-cache` | Remove model, log, and result files. |
| `make clear-all` | Remove both generated data and cached outputs. |
| `make help` | Show the available Make targets. |

## Limitations

Several methodological considerations are important when interpreting the project results.

**Data availability and revisions:** Economic publication lags are approximated using reporting frequencies rather than reconstructed from historical publication calendars. Consequently, the evaluation does not fully reproduce historical real-time data availability or statistical revisions.

**Mixed reporting frequencies:** Economic indicators are published at different frequencies. Converting these into a monthly forecasting dataset requires temporal alignment and, where appropriate, carrying available observations forward.

**Missing economic indicators:** Economic data availability differs between countries. Historical imputation and feature eligibility requirements help manage missing values, but they cannot recover information that was not originally reported.

**Forecasting assumptions:** Models are fitted using an initial historical sample and updated with newly available observations without repeated parameter estimation. Forecasting performance may therefore be affected by structural changes occurring after initial training.

**Geographic scope:** The study considers six selected EU countries rather than the entire EU. Results should not automatically be generalized to other migration corridors.

**Interpretation:** The study evaluates predictive relationships, not causal effects of macroeconomic conditions on migration. Immigration data also follow the country classifications of their underlying statistical sources.

## License 

This repository is distributed under the terms specified in its [LICENSE](LICENSE) file. The underlying statistical datasets remain subject to their respective providers' licensing and attribution requirements. Refer to the [Data README](data/README.md) for more information.