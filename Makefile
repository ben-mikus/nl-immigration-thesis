
.PHONY: all data get-data baseline clear-data clear-cache clear-all help results


# -- Main targets -----------------------------------------------------------------------------

all: clear-all data split train predict results

data:
	python3 -m src.data

split: data
	python3 -m src.split

train: split
	python3 -m src.train

predict: train
	python3 -m src.predict

results: predict
	python3 -m src.results


# -- Utilities --------------------------------------------------------------------------------

clear-all: clear-cache clear-data

clear-cache:
	rm -rf models/*
	rm -rf logs/*
	rm -rf results/*

clear-data:
	rm -f data/raw/*.csv
	rm -f data/processed/*.csv

help:
	@echo "Main targets:"
	@echo "  all        	Run the full pipeline from a fresh cache."
	@echo "  data       	Prepare the data directory and download the dataset."
	@echo "  split      	Split the preprocessed data into train/test sets."
	@echo "  train      	Train the forecasting models."
	@echo "  predict    	Generate predictions using the trained models."
	@echo "  results    	Display metrics and create forecast comparison charts."

	@echo "Utilities:"
	@echo "clear-all		Clean both data files and cache."
	@echo "clear-cache		Clean models/, logs/, and results/ subdirectories."
	@echo "clear-data		Remove downloaded data files."
	@echo "help				Show this help message."