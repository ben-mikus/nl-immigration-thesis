# Ethical, Legal, and Societal Aspects (ELSA) Report

## 1. Societal Relevance and Stakeholder Identification

Migration plays an important role in the demographic and economic development of the Netherlands, influencing labor supply, housing demand, infrastructure, and public services. Accurate immigration forecasts could therefore provide valuable information to policymakers, municipalities, businesses, and researchers seeking to understand future migration patterns.

This project investigates the effectiveness of statistical and machine learning models in forecasting monthly immigration associated with selected European Union countries into the Netherlands. Its primary objective is scientific rather than operational: to evaluate forecasting accuracy across different prediction horizons, economic conditions, and combinations of macroeconomic indicators.

The principal stakeholders are researchers who may build upon the findings and public institutions that could eventually benefit from improved forecasting methods. Immigrants and receiving communities are indirect stakeholders, as they could be affected by how migration forecasts are interpreted or incorporated into public decisions.

Although the project does not directly inform policy decisions, its potential societal relevance warrants consideration of the ethical implications of forecasting migration, particularly concerning the interpretation and communication of results.

## 2. ELSA Analysis, Mitigation Strategies, and Implications

### 2.1. Social Interpretation and Potential Stigmatization

The most significant ethical concern associated with this project is the potential misinterpretation of country-specific immigration forecasts. Immigration is a politically sensitive subject, and public perceptions of migrants can be influenced by negative stereotypes. Consequently, forecasts indicating increasing immigration from a particular country could be interpreted negatively, potentially reinforcing unfavorable perceptions of migrants from that country.

However, the forecasting models do not evaluate the desirability of immigration or the social and economic contributions of individual migrants. They predict aggregate monthly immigration counts based on historical patterns and selected economic indicators. A predicted increase in immigration should therefore not be interpreted as evidence of either positive or negative societal consequences.

To mitigate this risk, the research should communicate its findings using neutral terminology and clearly distinguish numerical predictions from judgments about immigration. Conclusions should remain limited to forecasting performance rather than extending to unsupported claims about the characteristics or societal impacts of migrants.

### 2.2. Forecast Reliability and Misinterpretation

A second concern relates to the reliability of the forecasts and the consequences of presenting predictions without sufficient context. Migration is influenced by numerous economic, political, and social factors, many of which may not be captured by the selected predictors. Consequently, forecasting errors are unavoidable, particularly when economic conditions or migration patterns change.

If forecasts were interpreted as definitive predictions, they could contribute to poorly informed planning decisions or misleading public discussions.

The project's evaluation framework partially addresses this concern through chronological walk-forward evaluation, which assesses forecasting performance on observations not used for model fitting. Comparing forecasting errors across one-, three-, and six-month horizons and different Dutch business-cycle conditions also provides evidence about the circumstances under which predictions are more or less reliable.

Nevertheless, these evaluations cannot guarantee future accuracy. Results should therefore be accompanied by appropriate performance metrics and an explicit acknowledgment of the limitations of the forecasting models.

### 2.3. Data Representativeness and Transparency

The project uses publicly available, aggregated immigration statistics from Statistics Netherlands (CBS), supplemented by macroeconomic indicators from CBS and Eurostat. Because the analysis does not involve individual-level personal records, direct privacy risks are limited.

However, aggregated data introduces interpretive limitations. The immigration records describe monthly migration associated with selected countries without distinguishing between individual migration motives. Consequently, the project cannot establish whether observed or predicted changes are attributable specifically to labor migration, family reunification, education, or other motivations.

These limitations should be explicitly documented to prevent conclusions from extending beyond the available evidence. Transparency is further supported by documenting the data sources, preprocessing procedures, forecasting methods, and evaluation framework in the project's repository.

### 2.4. Legal Considerations

The project relies on publicly available statistical datasets rather than personally identifiable information. Accordingly, its design presents limited direct risks concerning personal data protection.

Nevertheless, public availability does not automatically remove all legal obligations. The applicable terms of use, attribution requirements, and redistribution conditions for CBS and Eurostat data should be respected.

As the project does not make decisions concerning individual migrants, it does not directly determine immigration eligibility, employment opportunities, or access to public services. The legal implications of deploying a forecasting system within an operational policy environment would require separate consideration.

## 3. Personal Stance on Project Implementation

I consider the research itself ethically appropriate and scientifically worthwhile. Its primary purpose is to investigate the forecasting capabilities of statistical and machine learning methods rather than to influence immigration policy directly. The use of aggregated public data limits individual privacy concerns, while the comparative evaluation of forecasting methods may contribute to a better understanding of the predictability of intra-EU migration.

Nevertheless, the research carries potential societal risks, particularly concerning the interpretation of country-specific forecasts and the possibility of reinforcing negative perceptions of immigrants. These risks can be reduced through neutral communication, transparent reporting of model limitations, and careful interpretation of forecasting results.

I distinguish between conducting the research and implementing its findings in practice. While I consider the research suitable for academic publication, I would not recommend immediate operational deployment based solely on the current research design. Such implementation would require additional validation across countries and time periods, an assessment of forecasting reliability, and consideration of the consequences of decisions informed by the predictions.

Ultimately, I consider the project desirable as a research demonstration, provided that its findings are presented transparently and remain within the limitations established by the empirical evaluation.
