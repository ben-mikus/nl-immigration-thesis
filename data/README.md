# Data

The dataset ingested into this directory via the `make data` command supports the thesis project **Forecasting Intra-EU Migration to the Netherlands**. The study compares forecasts of monthly immigration at horizons of one, three, and six months and examines whether economic indicators improve forecasting performance. The current dataset covers Bulgaria, Poland, and Romania, allowing country-specific forecasting comparisons.

## Source

The derived dataset, `panel_data.csv`, combines public aggregate statistics from Statistics Netherlands (CBS) with a Dutch business-cycle indicator. The dataset is built using the  separate [nl-immigration-data](https://github.com/ben-mikus/nl-immigration-data) repository. For source tables, API filters, and output period, see [`config.py`](https://github.com/ben-mikus/nl-immigration-data/blob/main/config.py); for the countries and indicators currently selected, see [`settings.py`](https://github.com/ben-mikus/nl-immigration-data/blob/main/settings.py).

### Dataset Coverage and Structure

The current exported file contains **576 rows** and **4 columns**, covering **January 2010** through **December 2025**, inclusive. Each row represents one month for one of three origin-country labels: Bulgaria, Poland, or Romania (192 months per country). The supplied file has no missing values or duplicate `Period`–`Country` combinations.

| Column | Description | Source Frequency |
| --- | --- | --- |
| `Period` | Observation month, encoded as `YYYYMM`, e.g. `201001`. | Monthly |
| `Country` | Country label: `Bulgaria`, `Poland`, or `Romania`.  | N/A |
| `Immigration` | CBS monthly immigration count for the configured origin/migration-background category; the forecasting target. | Monthly |
| `NL-CONJCLK`  | Dutch CBS Conjunctuurklok business-cycle indicator, shared across countries for each month. | Monthly |

### Source Selections

| Source | Dataset and Configuration |
| --- | --- |
| CBS Immigration | Tables [85484NED](https://opendata.cbs.nl/#/CBS/nl/dataset/85484NED/table) and [83518NED](https://opendata.cbs.nl/#/CBS/nl/dataset/83518NED/table), measure `M000167`, monthly periods, country codes `H008567`, `H008718`, and `H008723`, and sex code `T001038`. Table 85484NED uses `Herkomstland` and `Geboorteland=T001638`; table 83518NED uses `Migratieachtergrond` and `Generatie=T001040`. |
| CBS Business Cycle | Downloaded from the [CBS Conjunctuurklok dashboard](https://www.cbs.nl/nl-nl/visualisaties/dashboard-economie/conjunctuurklok) and supplied to the builder as `table-conjunctuur-indicator.csv`. |

The builder combines the series using `Period` and `Country`.

## Licence

The underlying data retain their source reuse terms:
- CBS: its [copyright policy](https://www.cbs.nl/nl-nl/over-ons/website/copyright) applies CC BY 4.0 unless otherwise stated. Credit CBS and identify adaptations; attribution must not imply CBS endorsement.

Suggested attribution: **Source: CBS and Eurostat; selection and alignment by Benjamin Mikus**. This combined panel is an adapted dataset. Eurostat is not responsible for the transformations or conclusions of this project. These data reuse terms are separate from any licence covering repository code.

## How to get it

After properly cloning and configuring this repository, running `make data` will generate the dataset in `data/` as `data.csv`.

## Known limitations

- Country definition: the immigration configuration uses CBS Herkomstland and the older Migratieachtergrond classification. For example, the label Poland should not be interpreted automatically as Polish nationality or previous residence in Poland. The exact birth-country/generation selections and comparability of the two CBS tables should be checked against their metadata before interpreting the series as a bilateral flow.
- Limited scope: the current dataset covers three countries across 576 months. Results cannot automatically be generalized to other EU countries or migration flows. The aggregate target does not distinguish migration motives.
- Mixed frequencies: repeated quarterly and half-yearly values do not provide genuinely monthly economic measurements and may obscure changes within those periods.
- Publication timing: alignment to an observation month does not establish that an indicator was available at that month's forecast origin. Forecast evaluation should account for release delays and avoid using future information.
- Historical revisions: CBS, Eurostat, and the Conjunctuurklok can revise earlier observations. The panel is not documented as a real-time vintage dataset. CBS notes that its business-cycle series uses updated information and that its methodology was revised in October 2024.
- Metadata retention: the final eight-column CSV does not contain source status flags, release dates, retrieval timestamps, or table-of-origin fields. No missing values in this file does not by itself establish uniform quality or final status of the underlying observations.
