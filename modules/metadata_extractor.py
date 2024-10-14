# modules/metadata_extractor.py

"""
metadata_extractor.py

This module handles the extraction of metadata from media files, such as images. It
extracts information like timestamps and GPS data which are used for organizing files.

Functions:
- extract_image_metadata(image_path, settings): Extracts metadata from an image file.
"""

import logging
from PIL import Image, ExifTags


def extract_image_metadata(image_path, settings):
    """
    Extracts metadata from an image file, including timestamp and GPS data.

    Parameters:
    - image_path (str): Path to the image file.
    - settings (dict): User-defined settings.

    Returns:
    - dict or None: Dictionary containing metadata or None if extraction fails.
    """
    metadata = {}
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()

        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                metadata[tag_name] = value

        # Get timestamp
        metadata['timestamp'] = metadata.get('DateTimeOriginal') or metadata.get('DateTime')

        # Get GPS data
        gps_info = metadata.get('GPSInfo')
        if gps_info:
            gps_data = {}
            for key in gps_info.keys():
                decode = ExifTags.GPSTAGS.get(key, key)
                gps_data[decode] = gps_info[key]
            metadata['gps'] = gps_data

        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from {image_path}: {e}")
        return None
