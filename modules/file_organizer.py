"""
file_organizer.py

This module handles the renaming and organizing of media files based on
their metadata, such as timestamps and location. It structures the
organized files into directories by year and month.

Functions:
- rename_and_organize(file_path, timestamp, location, output_dir): Renames and moves the file to the appropriate directory.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

def rename_and_organize(file_path, timestamp, location, output_dir):
    """
    Renames and moves a media file based on its timestamp and location.

    Parameters:
    - file_path (str): Path to the media file.
    - timestamp (str or None): The timestamp extracted from metadata.
    - location (str or None): The human-readable location extracted from GPS data.
    - output_dir (str): Base directory where organized files will be stored.

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
        
        year_month = date_obj.strftime('%Y-%m')
        date_str = date_obj.strftime('%Y%m%d_%H%M%S')
        location_str = location.replace(' ', '_').replace(',', '') if location else "unknown_location"

        # Define target directory based on year and month
        target_dir = os.path.join(output_dir, date_obj.strftime('%Y'), year_month)
        os.makedirs(target_dir, exist_ok=True)

        # Create new filename
        new_filename = f"{date_str}_{location_str}{Path(file_path).suffix}"
        new_file_path = os.path.join(target_dir, new_filename)

        # Move and rename the file
        shutil.move(file_path, new_file_path)
        logging.info(f"File moved and renamed to: {new_file_path}")
        return new_file_path
    except Exception as e:
        logging.error(f"Error organizing file {file_path}: {e}")
        return None
