```mermaid
flowchart TD
    START(["make all"]) --> CLEAN["Makefile: clear-all<br/>Clear previous data, models, logs and results"]
    CLEAN --> SOURCE[("nl-immigration-data<br/>panel_data.csv")]

    subgraph PREP["1 · DATA PREPARATION"]
        DATA["src.data<br/>Filter countries and features<br/>Apply economic publication lags"]
        PROCESSED[("data/processed/data.csv")]
        SPLIT["src.split<br/>Chronological country-level split"]
        TRAINCSV[("train.csv")]
        TESTCSV[("test.csv")]
        DATA --> PROCESSED --> SPLIT
        SPLIT --> TRAINCSV
        SPLIT --> TESTCSV
    end

    SOURCE --> DATA

    subgraph FIT["2 · MODEL TRAINING — src.train"]
        TRAIN["For each configured country"]
        BASE["Baseline<br/>Autoregressive model"]
        SELECT["src.features<br/>Forward selection using<br/>training-only validation"]
        ARX["AR-X Fourier<br/>Scale selected economics<br/>Fit regression"]
        RF["Random Forest<br/>Generate lag and Fourier features<br/>Fit regressor"]
        ART[("models/*.pkl<br/>Models, scalers, selections")]
        TRAIN --> BASE
        TRAIN --> SELECT
        SELECT --> ARX
        SELECT --> RF
        BASE --> ART
        ARX --> ART
        RF --> ART
    end

    TRAINCSV --> TRAIN

    subgraph EVAL["3 · FORECASTING — src.predict"]
        PRED["Load country models<br/>and training/test panels"]
        LOOP["Walk-forward origins<br/>for each test month"]
        FC["Forecast horizons<br/>1, 3 and 6 months"]
        UPDATE["Append newly available<br/>immigration observations<br/>without refitting"]
        FORECASTS[("results/forecasts.csv")]
        PRED --> LOOP --> FC
        FC --> UPDATE
        UPDATE -->|"Next origin"| LOOP
        FC -->|"Collect valid forecasts"| FORECASTS
    end

    ART --> PRED
    TRAINCSV --> PRED
    TESTCSV --> PRED

    subgraph OUTPUT["4 · RESULTS — src.results"]
        RESULTS["Calculate forecast errors<br/>and produce visualizations"]
        METRICS[("results/metrics.csv<br/>MAE, WAPE, counts")]
        PLOTS[("Forecast comparison PNGs<br/>Country-level and summary")]
        RESULTS --> METRICS
        RESULTS --> PLOTS
    end

    FORECASTS --> RESULTS
    TRAINCSV --> RESULTS
    TESTCSV --> RESULTS
    ART -->|"Selected feature names"| RESULTS

    CONFIG["src.config<br/>Countries, features, lags,<br/>horizons, model settings"] -.-> DATA
    CONFIG -.-> SPLIT
    CONFIG -.-> TRAIN
    CONFIG -.-> PRED
    CONFIG -.-> RESULTS
  ```