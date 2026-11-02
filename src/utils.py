### src/utils.py
"""
src.utils contains utility functions that are used across different modules in the project. Currently, the only function
is ``build_logger``, which sets up logging to both a file and the console.
"""


import logging
import os


def build_logger():
    """Enables shared logging across modules by creating a pre-configured logger object.
    
    Returns:
        logging.Logger: A pre-configured logger object.
    
    Notes
    -----
    The logger writes messages to both a file located at ``logs/pipeline.log`` and the console. All callers receive the
    the same logger name because __name__ refers to this utilities module rather than the module calling the logger. The
    logging level is set to INFO by default. This module cannot be run on its own and is intended to be imported.
    """


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
