# modules/metadata_extractor.py

import logging
from datetime import datetime
import os
import subprocess
import json
from pathlib import Path
import shutil  # Import shutil to use shutil.which

def extract_image_metadata(image_path, settings):
    """
    Extracts metadata from an image file, including timestamp and GPS data if available.

    Parameters:
    - image_path (str): Path to the image file.
    - settings (dict): User-defined settings.

    Returns:
    - dict or None: Dictionary containing metadata or None if extraction fails.
    """
    metadata = {}
    try:
        image_path = Path(image_path)

        # Check if image file exists
        if not image_path.is_file():
            logging.error(f"Image file does not exist: {image_path}")
            return None

        # Locate ExifTool using shutil.which
        exiftool_path = shutil.which('exiftool.exe') or shutil.which('exiftool')
        if not exiftool_path:
            logging.error("ExifTool executable not found in PATH.")
            return None
        else:
            logging.info(f"ExifTool found at: {exiftool_path}")

        # Log the command being executed
        command = [exiftool_path, '-j', str(image_path)]
        logging.info(f"Running command: {' '.join(command)}")

        # Use ExifTool for all image formats, including HEIC
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            logging.error(f"ExifTool error for {image_path}: {result.stderr}")
            return None

        # Parse ExifTool JSON output
        exif_data = json.loads(result.stdout)[0]

        # Extract timestamp
        timestamp = exif_data.get('DateTimeOriginal') or exif_data.get('CreateDate') or exif_data.get('ModifyDate')
        if timestamp:
            metadata['timestamp'] = timestamp
        else:
            # Fallback to file's last modification time
            metadata['timestamp'] = datetime.fromtimestamp(image_path.stat().st_mtime).strftime('%Y:%m:%d %H:%M:%S')

        # Log extracted metadata
        logging.info(f"Metadata extracted for {image_path}: {json.dumps(exif_data, indent=2)}")

        # Extract GPS data
        latitude = exif_data.get('GPSLatitude')
        latitude_ref = exif_data.get('GPSLatitudeRef')
        longitude = exif_data.get('GPSLongitude')
        longitude_ref = exif_data.get('GPSLongitudeRef')

        if latitude and latitude_ref and longitude and longitude_ref:
            decimal_latitude = _convert_to_decimal(latitude, latitude_ref)
            decimal_longitude = _convert_to_decimal(longitude, longitude_ref)
            metadata['gps'] = {
                'latitude': decimal_latitude,
                'longitude': decimal_longitude
            }
            logging.info(f"GPS data extracted: {metadata['gps']}")
        else:
            metadata['gps'] = None
            logging.warning(f"No complete GPS data found for {image_path}")

        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from {image_path}: {e}")
        return None

def _convert_to_decimal(value, ref):
    """
    Convert GPS coordinates to decimal degrees.

    Parameters:
    - value: GPS coordinate value (float or string).
    - ref: Reference direction ('N', 'S', 'E', 'W').

    Returns:
    - float: Decimal degree representation of the coordinate.
    """
    try:
        # Handle different formats returned by ExifTool
        if isinstance(value, list):
            # Example: ['40 deg 48\' 39.43" N']
            dms = value
            # Assuming the first element is the coordinate string
            coord_str = dms[0]
            parts = coord_str.replace(' deg ', ' ').replace("' ", ' ').replace('"', '').split()
            if len(parts) < 4:
                logging.error(f"Unexpected GPS coordinate format: {coord_str}")
                return None
            degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            ref_direction = parts[3]
        elif isinstance(value, str):
            # Example: "40 deg 48' 39.37\" N"
            coord_str = value
            parts = coord_str.replace(' deg ', ' ').replace("' ", ' ').replace('"', '').split()
            if len(parts) < 4:
                logging.error(f"Unexpected GPS coordinate format: {coord_str}")
                return None
            degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            ref_direction = parts[3]
        else:
            # Assuming value is a numeric float already
            decimal = float(value)
            ref_direction = ref
            return decimal * (-1) if ref_direction.upper() in ['S', 'W'] else decimal

        # Convert DMS to decimal degrees
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        # Apply negative sign for South and West
        if ref_direction.upper() in ['S', 'W']:
            decimal = -decimal

        return decimal
    except Exception as e:
        logging.error(f"Error converting GPS coordinates: {e}")
        return None
