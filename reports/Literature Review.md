# Forecasting Intra–EU Migration to the Netherlands

*Benjamin Mikus*
## Problem Statement

Demographic change, including migration, has important implications for the planning of Dutch housing, infrastructure, and public services (State Commission Demographic Developments 2050, 2024). Anticipating short-term migration flows can therefore support policy preparedness by providing policymakers with additional information for monitoring changing arrival patterns and informing broader planning.

This project forecasts total monthly immigration from selected European Union (EU) countries to the Netherlands using migration history and macroeconomic conditions. It covers all migration motives, with conclusions restricted to the flows evaluated. The study will combine monthly immigration records with economic indicators from CBS and Eurostat, covering approximately 2005 to 2026. Forecasts one, three, and six months ahead will be evaluated using traditional statistical and machine learning approaches. Beyond comparing forecasting accuracy, the project will examine performance across Dutch business-cycle conditions and assess whether additional origin-country and destination-country indicators improve predictions beyond a model using historical migration and Dutch business-cycle conditions.



## Literature Review

Recent advancements in asylum and refugee migration forecasting demonstrate the potential of adaptive models and machine learning, offering a methodological starting point for examining intra–EU migration. Carammia et al. (2022) combine administrative records, event data, and internet searches using Dynamic Elastic Net, achieving an average relative error of 7% for four-week-ahead forecasts of Syrian asylum applications in Germany, compared with 15.2% for ARIMA. Similarly, Bosco et al. (2024) compare neural networks, Random Forest, and XGBoost when forecasting asylum applications in Italy, exceeding an explained variance in validation of 0.80 across all three models. Then, Boss et al. (2024) extend the comparison of models to monthly asylum flows from 150 origin countries to the EU27, finding that a Random Forest-XGBoost ensemble outperforms alternatives including Elastic Net and a random-walk benchmark across three-, six-, and twelve-month horizons.

These studies support testing adaptive models and ensembles, however, differences in targets, predictors, and horizons prevent direct comparisons. Additionally, it fails to establish whether one universally accepted state-of-the-art framework exists within migration forecasting. Furthermore, predictor relevance has shown to vary across migration process. Soto Nishimura and Czaika (2022) find that the importance and direction of migration drivers differ across labor, family, student, asylum, and irregular migration. For example, non-traditional, digital data was found to supplement traditional sources when predicting forced displacement in the study from Henningsen (2025), while Dragomir-Constantin et al. (2025) concluded that migration within the EU is governed by interactions among traditional socioeconomic estimators through the use of explainable decision-tree models.

Research specifically on intra–EU migration echoes this fact and provides more direct guidance on potential predictors. Using data from 23 countries, Afonso et al. (2025) applied Bayesian model averaging and quantile regression and found that earnings differences are informative in identifying migration flows alongside past migration flows themselves., Landesmann et al. (2015), identified previous migration and real wage differentials as prominent influences of migration through the use of panel VAR. Barker and Bijak (2025) additionally demonstrate that macroeconomic indicators contain useful information for short-term migration forecasting through their mixed-frequency Bayesian panel VAR, reporting a MAPE of approximately 1.9– 2.8% in their in-sample exercise.

Then, in the Dutch context, this distinction appears particularly relevant. Though studies addressing Dutch migration remain limited, technical papers emphasize the importance of economic pull factors. Analyzing migration over 70 years of Dutch migration data, van Stiphout-Kramer et al. (2024) concluded that labor demand has historically been the dominant driver of migration to the Netherlands. They further specified that labor migration closely follows the Dutch business cycle (van Stiphout-Kramer et al., 2024).



## Knowledge Gap and Scientific Contribution

The literature identifies relationships between economic conditions and European migration. However, the literature does not establish whether these findings extend to monthly immigration from selected EU countries to the Netherlands. The gains reported within the asylum forecasting literature motivate comparing machine learning with statistical benchmarks in this setting. Findings in the intra–EU literature further motivate testing whether additional origin-country and destination-country indicators improve forecasts beyond migration history and Dutch economic conditions. Finally, the relationship between Dutch migration and the business cycle also motivates evaluating forecasting gains across economic conditions. This study will therefore contribute evidence to when these methods and indicators improve predictive performance, including where added complexity provides no improvement. These comparisons lead to the following scientific baseline and research questions.

An autoregressive (AR) model, estimated by ordinary least squares using sktime’s AutoREG, will provide the statistical baseline, predicting immigration from its lagged observations.



**RQ1** – How does the forecasting performance of modern machine learning approaches compare with those of a traditional statistical model in predicting monthly migration flows into the Netherlands one, three, and six months ahead?



**RQ2** – How does the relative forecasting performance of the selected models vary across favorable and unfavorable phases of the Dutch business cycle?



**RQ3** – How does the inclusion of additional destination-country and origin country macroeconomic indicators beyond GDP growth affect the forecasting accuracy and generalization performance of models predicting monthly migration flows.

## Table 1 – Comparison of Forecasting Studies

| Study | Target and predictors | Models and evaluation | Principal result | Relevance to this project |
|---|---|---|---|---|
| Carammia et al. (2022) | Weekly asylum applications by origin and destination; administrative records, events, internet searches, and border crossings. | Adaptive Dynamic Elastic Net system; ARIMA benchmark; forecasts up to four weeks ahead; relative and absolute errors. | For Syrian applications in Germany, average relative error was 7% versus 15.2% for ARIMA; median relative error was 4% versus 14.7%. These are results for that particular flow. | Motivates testing additional predictors and adapting their selection over time. The reported accuracy cannot be transferred directly to monthly intra-EU immigration. |
| Bosco et al. (2024) | First-time asylum applications in Italy and Central Mediterranean border crossings; lagged migration measures and economic indicators, including price indices. | Neural networks, Random Forest, XGBoost, and a stacked ensemble; validation MAE and explained variance; forecasting up to six months ahead. | For Italian asylum applications, individual models exceeded 0.80 explained variance in validation, with the ensemble performing best. Past asylum applications were the most important predictor in the Random Forest analysis. | Supports retaining migration history and comparing individual models with ensembles. The asylum results should not be attributed to the border-crossing task. |
| Boss et al. (2024) | Monthly asylum flows from 150 origin countries to the EU27; conventional indicators and Google Trends variables. | Random Forest, XGBoost, Elastic Net, factor models, and ensembles; out-of-sample RMSE relative to a random walk, expressed as a Theil ratio. | The Random Forest–XGBoost ensemble outperforms the random walk at three- to twelve-month horizons. A Theil ratio below 1 indicates improvement over the benchmark. | Provides a model-comparison framework and emphasizes measuring gains against a credible baseline at each horizon. |
| Barker and Bijak (2025) | Immigration, emigration, and net migration rates; annual migration and quarterly macroeconomic observations. | Mixed-frequency Bayesian panel VAR; RMSE, MAE, MAPE, Theil’s U, and coverage of 67% predictive intervals; reported evaluation for 2018–2019. | Immigration and emigration have lower MAPE than net migration; forecast errors vary across countries. | Supports examining macroeconomic information and forecasting immigration separately. Its mixed-frequency evaluation differs from forecasting directly observed monthly arrivals. |



## References

Afonso, A., Alves, J., & Beck, K. (2025). Drivers of migration flows in the European Union:       Earnings or unemployment? International labour review, 164(2), 1–23.       https://doi.org/10.16995/ilr.18845

Barker, E., & Bijak, J. (2025). Mixed-frequency var: A new approach to predicting and        analysing future migration in Europe using macroeconomic data. Data & Policy,        7(e3). https://doi.org/10.1017/dap. 2024.82

Bijak, J., Vono de Vilhena, D., Potančoková, M., & Team, T. Q. (2023, July). White paper on         migration uncertainty: Towards foresight and preparedness (Discussion Paper No. 19).         Population Europe. Retrieved June 27, 2026, from https://population-         europe.eu/research/discussion papers/white-paper-migration-uncertainty

Bosco, C., Minora, U., Rosi´nska, A., Teobaldelli, M., & Belmonte, M. (2024). A machine        learning architecture to forecast irregular border crossings and asylum requests for        policy support in europe: A case study. Data & Policy, 6(e81).        https://doi.org/10.1017/dap.2024.48 Boss, K., Groeger, A., Heidland, T., Kruger, F., & Zheng, C. (2024). Forecasting bilateral        asylum seeker flows with high-dimensional data and machine learning techniques.        Journal of Economic Geography, 25(1), 3–19. https://doi.org/10.1093/jeg/lbae023

Carammia, M., Iacus, S. M., & Wilkin, T. (2022). Forecasting asylum-related migration flows      with machine learning and data at scale. Scientific Reports, 12, 1457.      https://doi.org/10.1038/s41598-022-05241-8

Dragomir-Constantin, F.-L., Beldiman, C. M., & Zlati, M. L. (2025). Informational       approaches in modelling social and economic relations: Study on migration and       access to services in the European Union. Systems, 13(6), 469.       https://doi.org/10.3390/systems13060469 Henningsen, G. (2025). Big data for the prediction of forced displacement. International       Migration Review, 59(1). https://doi.org/10.1177/ 01979183231195296

Landesmann, M., Leitner, S. M., & Mara, I. (2015, August). Intra-EU mobility and push and       pull factors in EU labour markets: Estimating a panel var model (wiiw Working Paper       No. 120). The Vienna Institute for International Economic Studies. Retrieved June 29,       2026, from https://wiiw.ac.at/intra-eu-mobility-and-push-and-pull-factors in-eu-       labour-markets-estimating-a-panel-var-model-dlp-3671.pdf

Soto Nishimura, A., & Czaika, M. (2022, September). Migration pathways into Europe: An        assessment of drivers and policies (Deliverable D5.7). Quant Mig Project. Retrieved        June 27, 2026, from https://www.quantmig. 9 references        eu/res/files/QuantMig%20D5.7%20Migration%20Pathways%        20V1.1%2030Sep2022.pdf

State Commission Demographic Developments 2050. (2024). Moderate growth: Report of        the State Commission Demographic Developments 2050. Retrieved September 23,        2026, from https://www.government.nl/documents/2024/01/15/moderate-growth

van Stiphout-Kramer, B., Hendriks, B., Meijerink, G., van der Plaat, M., & van Sonsbeek, J.-        M. (2024, August). Economic dynamics and migration (CPB Publication). CPB        Netherlands Bureau for Economic Policy Analysis.        https://doi.org/10.13140/RG.2.2.28899.16166