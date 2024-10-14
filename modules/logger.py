"""
logger.py

This module sets up and configures the logging for the Photo Organizer program.

Functions:
- setup_logging(log_file_path): Configures the logging settings.
"""

import logging
import os

def setup_logging(log_file_path):
    """
    Configures the logging settings for the program.

    Parameters:
    - log_file_path (str): Path to the log file.

    Returns:
    - None
    """
    try:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        logging.basicConfig(
            filename=log_file_path,
            filemode='a',
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        logging.info("Logging initialized.")
    except Exception as e:
        print(f"Failed to set up logging: {e}")
