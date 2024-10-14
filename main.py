"""
main.py

Entry point for the Photo Organizer program. It orchestrates the workflow by
utilizing functions from various modules to extract metadata, detect duplicates,
organize files, and handle videos.

Usage:
    python main.py --input_dir "C:\\Path\\To\\input_media" --output_dir "C:\\Path\\To\\output_media" --trash_dir "C:\\Path\\To\\trash_duplicates"
"""

# main.py

import os
import logging
from datetime import datetime
from tqdm import tqdm

from modules.logger import setup_logging
from modules.duplicate_detector import is_duplicate, handle_duplicate
from modules.metadata_extractor import extract_image_metadata
from modules.geolocation_mapper import reverse_geocode
from modules.file_organizer import rename_and_organize
from modules.video_handler import process_video

def organize_media(input_dir, output_dir, trash_dir, log_callback=None):
    """
    Organizes media files from input_dir to output_dir, moving duplicates to trash_dir.

    Parameters:
    - input_dir (str): Path to the input media directory.
    - output_dir (str): Path to the output directory.
    - trash_dir (str): Path to the trash directory for duplicates.
    - log_callback (function, optional): Function to call for logging messages.
    
    Returns:
    - None
    """
    setup_logging(os.path.join('logs', 'photo_organizer.log'))
    logging.info(f"Starting organization: Input - {input_dir}, Output - {output_dir}, Trash - {trash_dir}")
    
    processed_hashes = set()

    for root, _, files in os.walk(input_dir):
        for file in tqdm(files, desc="Processing files"):
            file_path = os.path.join(root, file)
            ext = file.lower()

            # Detect and handle duplicates
            if is_duplicate(file_path, processed_hashes):
                handle_duplicate(file_path, trash_dir)
                if log_callback:
                    log_callback(f"Duplicate moved to trash: {file_path}")
                continue

            if ext.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                # Process image
                metadata = extract_image_metadata(file_path)
                if metadata is None:
                    logging.warning(f"Skipping file due to metadata extraction failure: {file_path}")
                    if log_callback:
                        log_callback(f"Skipping (metadata extraction failed): {file_path}")
                    continue
                timestamp = metadata.get('timestamp')
                gps_data = metadata.get('gps')
                location = reverse_geocode(gps_data)

                new_file_path = rename_and_organize(file_path, timestamp, location, output_dir)
                if new_file_path:
                    logging.info(f"Image processed: {new_file_path}")
                    if log_callback:
                        log_callback(f"Image processed: {new_file_path}")

            elif ext.endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv')):
                # Process video
                new_file_path = process_video(file_path, output_dir)
                if new_file_path:
                    logging.info(f"Video processed: {new_file_path}")
                    if log_callback:
                        log_callback(f"Video processed: {new_file_path}")

            else:
                logging.warning(f"Unsupported file format: {file_path}")
                if log_callback:
                    log_callback(f"Unsupported format: {file_path}")
                continue

    logging.info("Organization completed.")
    if log_callback:
        log_callback("Organization completed.")
