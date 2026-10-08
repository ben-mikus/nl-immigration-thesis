#!/usr/bin/env bash
# This tells the system to use bash to interpret this script

# Safety flags - these make your script more robust:
set -euo pipefail
# -e: Exit immediately if any command fails (no silent failures)
# -u: Treat unset variables as errors (catch typos)
# -o pipefail: Ensure pipeline commands fail properly (detect failures in pipes)
# Why these flags matter: Without these flags, your script might continue running even after errors occur, leading to inconsistent or corrupted results. 
# This is especially critical for data processing scripts!

# Print status message to user
echo "[INFO] Preparing data directory structure..."

# Create data directory 
mkdir -p data
# -p flag: Create parent directories as needed, don't error if directory exists

RAW_FILE="data/data.csv"
curl -L -o $RAW_FILE https://raw.githubusercontent.com/ben-mikus/nl-immigration-data/main/data/panel_data.csv
echo "[INFO] Downloaded immigration dataset: $RAW_FILE"

# Verify that the download actually produced a non-empty file
if [ ! -s "$RAW_FILE" ]; then
    echo "[ERROR] Dataset download failed or produced an empty file."
    exit 1
fi

# Report some basic information
LINES=$(wc -l < "$RAW_FILE")

echo "[REPORT] Dataset has $LINES lines including the header."
echo "[INFO] Data preparation complete."