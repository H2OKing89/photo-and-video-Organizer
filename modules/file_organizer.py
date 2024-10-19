# modules/file_organizer.py

import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

def rename_and_organize(file_path, timestamp, location, location_found, output_dir, settings):
    """
    Renames and moves a media file based on its timestamp and location according to user settings.
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
        elif naming_convention == 'Dynamic':
            # In Dynamic mode, prioritize location if found, else use full address
            if location_found:
                new_filename = f"{date_str}_{location_str}{Path(file_path).suffix}"
            else:
                # Use full address or default to Unknown_Location
                new_filename = f"{date_str}_Unknown_Location{Path(file_path).suffix}"
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
