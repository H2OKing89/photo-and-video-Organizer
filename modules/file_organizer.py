# modules/file_organizer.py

"""
file_organizer.py

This module handles the renaming and organizing of media files based on
their metadata, such as timestamps and location. It structures the
organized files into directories by year and month.

Functions:
- rename_and_organize(file_path, timestamp, location, output_dir, settings): Renames and moves the file to the appropriate directory based on settings.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import logging


def rename_and_organize(file_path, timestamp, location, output_dir, settings):
    """
    Renames and moves a media file based on its timestamp and location according to user settings.

    Parameters:
    - file_path (str): Path to the media file.
    - timestamp (str or None): The timestamp extracted from metadata.
    - location (str or None): The human-readable location extracted from GPS data.
    - output_dir (str): Base directory where organized media will be stored.
    - settings (dict): User-defined settings for naming conventions.

    Returns:
    - str or None: The new file path if successful, else None.
    """
    try:
        if timestamp:
            try:
                date_obj = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                # Handle different timestamp formats if necessary
                date_obj = datetime.fromtimestamp(os.path.getmtime(file_path))
        else:
            date_obj = datetime.fromtimestamp(os.path.getmtime(file_path))

        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m')
        year_month = date_obj.strftime('%Y-%m')
        date_str = date_obj.strftime('%Y%m%d_%H%M%S')
        location_str = location.replace(' ', '_').replace(',', '') if location else "Unknown_Location"

        # Define target directory based on year and month
        target_dir = os.path.join(output_dir, year, year_month)
        os.makedirs(target_dir, exist_ok=True)

        # Create new filename based on naming convention
        naming_convention = settings.get('naming_convention', 'Date_Location')
        if naming_convention == 'Date_Location':
            new_filename = f"{date_str}_{location_str}{Path(file_path).suffix}"
        elif naming_convention == 'Date':
            new_filename = f"{date_str}{Path(file_path).suffix}"
        elif naming_convention == 'Location':
            new_filename = f"{location_str}{Path(file_path).suffix}"
        else:
            new_filename = f"{date_str}_{location_str}{Path(file_path).suffix}"  # Default

        new_file_path = os.path.join(target_dir, new_filename)

        # Move and rename the file
        shutil.move(file_path, new_file_path)
        logging.info(f"File moved and renamed to: {new_file_path}")
        return new_file_path
    except Exception as e:
        logging.error(f"Error organizing file {file_path}: {e}")
        return None
