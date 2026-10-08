# Data

The dataset ingested into this directory via the `make data` function supports the thesis project **Forecasting Intra-EU Migration to the Netherlands**. The study compares forecasts of monthly immigration at horizons of one, three, and six months and examines whether economic indicators improve forecasting performance. The current baseline dataset covers Poland; an intended narrow selection for ease of pipeline development.

## Source

The derived dataset, `panel_data.csv`, combines public aggregate statistics from Statistics Netherlands (CBS) and Eurostat. It was assembled using the separate [nl-immigration-data](https://github.com/ben-mikus/nl-immigration-data) repository. To view the specifications around the source tables, API filters, and output period, see the repository's [`config.py`](https://github.com/ben-mikus/nl-immigration-data/blob/main/config.py) file.

### Dataset Coverage and Structure

The supplied baseline file contains **192 rows** and **8 columns**, covering **January 2010** through **December 2025**, inclusive. Each row represents one month for Poland. The supplied file has no missing values or duplicate `Period`–`Country` combinations.

| Column | Description | Source frequency |
| --- | --- | --- |
| `Period` | Observation month, encoded as `YYYYMM`, e.g. `201001`. | Monthly |
| `Country` | Country label; `Poland` in the current file. | Not applicable |
| `Immigration` | CBS monthly immigration count for the configured Polish origin/migration-background category; the forecasting target. | Monthly |
| `Country-MINWAGE` | Polish national minimum wage in purchasing-power standards (PPS). | Half-yearly |
| `NL-MINWAGE` | Dutch national minimum wage in PPS. | Half-yearly |
| `Country-WAGESAL` | Polish wages-and-salaries Labour Cost Index, seasonally and calendar adjusted, 2020=100, NACE Rev. 2 sections B–S. | Quarterly |
| `NL-WAGESAL` | Equivalent Dutch wages-and-salaries Labour Cost Index. | Quarterly |
| `NL-CONJCLK` | Dutch CBS Conjunctuurklok business-cycle indicator. | Monthly panel series |

`Country-` identifies the Polish indicator and `NL-` identifies the Dutch benchmark. Country and Dutch values are retained separately; the builder does not calculate difference columns.

### Source Selections

| Source | Dataset and configuration |
| --- | --- |
| CBS immigration | Tables [85484NED](https://opendata.cbs.nl/#/CBS/nl/dataset/85484NED/table) and [83518NED](https://opendata.cbs.nl/#/CBS/nl/dataset/83518NED/table), measure `M000167`, monthly periods, country code `H008718`, and sex code `T001038`. Table 85484NED uses `Herkomstland` and `Geboorteland=T001638`; table 83518NED uses `Migratieachtergrond` and `Generatie=T001040`. |
| Eurostat minimum wage | [earn_mw_cur](https://ec.europa.eu/eurostat/databrowser/view/earn_mw_cur/default/table), `freq=S`, `currency=PPS`, countries `PL` and `NL`. |
| Eurostat Labour Cost Index | [lc_lci_r2_q](https://ec.europa.eu/eurostat/databrowser/view/lc_lci_r2_q/default/table), `freq=Q`, `s_adj=SCA`, `unit=I20`, `nace_r2=B-S`, `lcstruct=D11`, countries `PL` and `NL`. |
| CBS business cycle | Downloaded from the [CBS Conjunctuurklok dashboard](https://www.cbs.nl/nl-nl/visualisaties/dashboard-economie/conjunctuurklok) and supplied to the builder as `table-conjunctuur-indicator.csv`. |

The builder combines the series using `Period` and `Country`. Quarterly indicators are repeated across the three months of their quarter, and half-yearly indicators across the six months of their half-year. This creates a monthly aligned dataset without generating additional independent economic observations.

## Licence

The underlying data retain their source reuse terms:
- CBS: its [copyright policy](https://www.cbs.nl/nl-nl/over-ons/website/copyright) applies CC BY 4.0 unless otherwise stated. Credit CBS and identify adaptations; attribution must not imply CBS endorsement.
- Eurostat: its [reuse policy](https://ec.europa.eu/eurostat/web/main/help/copyright-notice) permits commercial and non-commercial reuse of statistical data with source acknowledgement, subject to stated exceptions. Identify modifications and retain dataset links when citing the data.
Suggested attribution: **Source: CBS and Eurostat; selection and alignment by Benjamin Mikus**. This combined panel is an adapted dataset. Eurostat is not responsible for the transformations or conclusions of this project. These data reuse terms are separate from any licence covering repository code.

## How to get it

After properly cloning and configuring this repository, running `make data` will generate the dataset in `data/` as `data.csv`.

## Known limitations

- Country definition: the immigration configuration uses CBS Herkomstland and the older Migratieachtergrond classification. The label Poland should not be interpreted automatically as Polish nationality or previous residence in Poland. The exact birth-country/generation selections and comparability of the two CBS tables should be checked against their metadata before interpreting the series as a bilateral flow.
- Limited scope: the current dataset covers one country and 192 months. Results cannot automatically be generalized to other EU countries or migration flows. The aggregate target does not distinguish migration motives.
- Mixed frequencies: repeated quarterly and half-yearly values do not provide genuinely monthly economic measurements and may obscure changes within those periods.
- Publication timing: alignment to an observation month does not establish that an indicator was available at that month's forecast origin. Forecast evaluation should account for release delays and avoid using future information.
- Historical revisions: CBS, Eurostat, and the Conjunctuurklok can revise earlier observations. The panel is not documented as a real-time vintage dataset. CBS notes that its business-cycle series uses updated information and that its methodology was revised in October 2024.
- Indicator interpretation: minimum wages measure statutory wage floors rather than average earnings. The Labour Cost Index measures change relative to 2020, rather than comparable wage levels across countries. NL-CONJCLK is a business-cycle indicator, not GDP growth.
- Metadata retention: the final eight-column CSV does not contain source status flags, release dates, retrieval timestamps, or table-of-origin fields. No missing values in this file does not by itself establish uniform quality or final status of the underlying observations.
