"""
video_handler.py

This module handles the processing of video files, including extracting
metadata and organizing them similarly to images.

Functions:
- process_video(video_path, output_dir): Processes a video file by extracting metadata and organizing it.
"""

import shutil
import os
from datetime import datetime
import logging
from .metadata_extractor import extract_video_metadata
from .geolocation_mapper import reverse_geocode
from .file_organizer import rename_and_organize

def process_video(video_path, output_dir):
    """
    Processes a video file by extracting metadata and organizing it.

    Parameters:
    - video_path (str): Path to the video file.
    - output_dir (str): Base directory where organized files will be stored.

    Returns:
    - str or None: The new file path if successful, else None.
    """
    try:
        metadata = extract_video_metadata(video_path)
        timestamp = metadata.get('timestamp')
        location = None  # Videos typically don't have GPS data, but could extract from separate sources if needed

        new_file_path = rename_and_organize(video_path, timestamp, location, output_dir)
        if new_file_path:
            logging.info(f"Video processed: {new_file_path}")
        return new_file_path
    except Exception as e:
        logging.error(f"Error processing video {video_path}: {e}")
        return None
