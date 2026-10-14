
.PHONY: all data get-data baseline clear-data help


# -- Main targets -----------------------------------------------------------------------------

all: clear-data get-data baseline

data:
	python3 -m src.data

split: data
	python3 -m src.split

train: split
	python3 -m src.train

predict: train
	python3 -m src.predict


# -- Utilities --------------------------------------------------------------------------------

clear-data:
	rm -f data/raw/*.csv
	rm -f data/processed/*.csv

clear-cache:
	rm -rf models/*
	rm -rf logs/*
	rm -rf results/*

help:
	@echo "Main targets:"
	@echo "  data       	Prepare the data directory and download the dataset."
	@echo "  split      	Split the preprocessed data into train/test sets."
	@echo "  train      	Train the forecasting models."
	@echo "  predict    	Generate predictions using the trained models."
	@echo "  results		Evaluate and display the forecasting results."

	@echo "Utilities:"
	@echo "clear-data		Remove downloaded data files."
	@echo "clear-cache		Clean models/, logs/, and results/ subdirectories."
	@echo "help				Show this help message."