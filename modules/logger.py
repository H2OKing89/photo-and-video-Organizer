# modules/logger.py

"""
logger.py

Logging module for the Photo and Video Organizer program. It sets up and configures
the logging settings to capture informational messages, warnings, errors, and debug
information. Logs are written to a designated log file for tracking and troubleshooting.

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
        # Ensure the log directory exists
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Check if handlers are already set to prevent duplication
        logger = logging.getLogger()
        if not logger.handlers:
            # Configure logging to file
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)

            # Configure logging to console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)

            # Add handlers to the logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

            # Set the logging level
            logger.setLevel(logging.INFO)

            logger.info("Logging initialized.")

    except Exception as e:
        print(f"Failed to set up logging: {e}")
