"""
video_handler.py

This module handles the processing of video files, including extracting
metadata and organizing them similarly to images based on user settings.

Functions:
- process_video(video_path, output_dir, settings): Processes a video file by extracting metadata and organizing it.
"""

import logging
from pymediainfo import MediaInfo
from .file_organizer import rename_and_organize  # Use relative import
from .geolocation_mapper import reverse_geocode  # Use relative import if needed

def extract_video_metadata(video_path, settings):
    """
    Extracts metadata from a video file, including timestamp and GPS data if available.

    Parameters:
    - video_path (str): Path to the video file.
    - settings (dict): User-defined settings.

    Returns:
    - dict or None: Dictionary containing metadata or None if extraction fails.
    """
    metadata = {}
    try:
        media_info = MediaInfo.parse(video_path)
        for track in media_info.tracks:
            if track.track_type == 'General':
                metadata['timestamp'] = track.recorded_date
            elif track.track_type == 'Video':
                # Extract GPS data if available
                # Note: Videos typically do not contain GPS metadata
                pass

        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from video {video_path}: {e}")
        return None

def process_video(video_path, output_dir, settings):
    """
    Processes a video file by extracting metadata and organizing it based on settings.

    Parameters:
    - video_path (str): Path to the video file.
    - output_dir (str): Path to the output directory where organized videos will be stored.
    - settings (dict): User-defined settings.

    Returns:
    - str or None: The new file path if successful, else None.
    """
    try:
        metadata = extract_video_metadata(video_path, settings)
        timestamp = metadata.get('timestamp')
        location = None  # Videos typically don't have GPS data

        new_file_path = rename_and_organize(video_path, timestamp, location, output_dir, settings)
        if new_file_path:
            logging.info(f"Video processed: {new_file_path}")
        return new_file_path
    except Exception as e:
        logging.error(f"Error processing video {video_path}: {e}")
        return None
