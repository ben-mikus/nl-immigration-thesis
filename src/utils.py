### src/utils.py
"""Modularizes logging setup for ease of use in other modules."""

import logging
import os


def build_logger():
    """Sets up logging to both a file and the console."""

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/pipeline.log"),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)