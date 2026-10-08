
.PHONY: data help

get-data:
	./scripts/prep_data.sh

clear-data:
	rm -f data/*.csv

help:
	@echo "Available targets:"
	@echo "  get-data    Prepare the data directory and download the dataset."
	@echo "  clear-data  Remove downloaded data files."
	@echo "  help        Show this help message."