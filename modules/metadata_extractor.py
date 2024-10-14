"""
metadata_extractor.py

This module handles the extraction of metadata from image and video files.
For images, it extracts EXIF data such as timestamps and GPS information.
For videos, it extracts metadata like recording dates.

Functions:
- extract_image_metadata(image_path): Extracts EXIF metadata from an image.
- extract_video_metadata(video_path): Extracts metadata from a video file.
"""

from PIL import Image, ExifTags
from pymediainfo import MediaInfo
import logging

def extract_image_metadata(image_path):
    """
    Extracts metadata from an image file.

    Parameters:
    - image_path (str): Path to the image file.

    Returns:
    - dict: A dictionary containing extracted metadata (timestamp, GPS data).
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
        metadata['timestamp'] = metadata.get('DateTimeOriginal')

        # Get GPS data
        gps_info = metadata.get('GPSInfo')
        if gps_info:
            gps_data = {ExifTags.GPSTAGS.get(t, t): gps_info[t] for t in gps_info}
            metadata['gps'] = gps_data

        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from {image_path}: {e}")
        return None

def extract_video_metadata(video_path):
    """
    Extracts metadata from a video file.

    Parameters:
    - video_path (str): Path to the video file.

    Returns:
    - dict: A dictionary containing extracted metadata (timestamp).
    """
    metadata = {}
    try:
        media_info = MediaInfo.parse(video_path)
        for track in media_info.tracks:
            if track.track_type == 'General':
                # Extracting the earliest available date
                metadata['timestamp'] = (
                    track.recorded_date or 
                    track.tagged_date or 
                    track.encoded_date
                )
        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from {video_path}: {e}")
        return None
