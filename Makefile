
.PHONY: all data get-data baseline clear-data help


# -- Main targets -----------------------------------------------------------------------------

all: clear-data get-data baseline

data:
	python3 -m src.data

baseline:
	python3 -m src.baseline


# -- Utilities --------------------------------------------------------------------------------

clear-data:
	rm -f data/raw/*.csv
	rm -f data/processed/*.csv

help:
	@echo "Available targets:"
	@echo "  data        Prepare the data directory and download the dataset."
	@echo "  baseline    Evaluate and refit the autoregression baseline."
	@echo "  all         Download data and run the complete baseline pipeline."
	@echo "  clear-data  Remove downloaded data files."
	@echo "  help        Show this help message."