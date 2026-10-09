
.PHONY: all data get-data baseline clear-data help

all: clear-data get-data baseline

data: get-data

get-data:
	./scripts/prep_data.sh

baseline:
	python3 -m src.baseline

clear-data:
	rm -f data/*.csv

help:
	@echo "Available targets:"
	@echo "  get-data    Prepare the data directory and download the dataset."
	@echo "  baseline    Evaluate and refit the autoregression baseline."
	@echo "  all         Download data and run the complete baseline pipeline."
	@echo "  clear-data  Remove downloaded data files."
	@echo "  help        Show this help message."