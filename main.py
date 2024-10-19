# main.py

import os
import logging
from modules.duplicate_detector import is_duplicate, handle_duplicate
from modules.metadata_extractor import extract_image_metadata
from modules.geolocation_mapper import reverse_geocode
from modules.file_organizer import rename_and_organize
from modules.video_handler import process_video
import pillow_heif  # Ensure HEIC support is registered

# Register HEIC opener with Pillow for handling HEIC files
pillow_heif.register_heif_opener()

def organize_media(input_dir, output_dir, trash_dir, log_callback=None, settings=None, progress_callback=None, status_callback=None, pause_event=None, cancel_event=None):
    """
    Organizes media files from input_dir to output_dir, moving duplicates to trash_dir.
    """
    try:
        logging.info(f"Starting organization: Input - {input_dir}, Output - {output_dir}, Trash - {trash_dir}")

        processed_hashes = set()

        # Calculate total number of files for progress tracking
        total_files = sum(len(files) for _, _, files in os.walk(input_dir))
        processed = 0

        for root, _, files in os.walk(input_dir):
            for file in files:
                # Check for cancellation
                if cancel_event and cancel_event.is_set():
                    logging.info("Organization process was cancelled by the user.")
                    if log_callback:
                        log_callback("Organization process was cancelled.")
                    return

                # Handle pausing
                if pause_event and pause_event.is_set():
                    logging.info("Organization process is paused.")
                    if log_callback:
                        log_callback("Organization process is paused.")
                    while pause_event.is_set():
                        pause_event.wait(1)  # Wait until the pause_event is cleared
                    logging.info("Organization process is resumed.")
                    if log_callback:
                        log_callback("Organization process is resumed.")

                processed += 1

                file_path = os.path.join(root, file)
                ext = file.lower()

                # Update progress
                if progress_callback and total_files > 0:
                    progress = int((processed / total_files) * 100)
                    progress_callback(progress)

                # Update status
                if status_callback:
                    status_message = f"Processing file {processed} of {total_files}: {file}"
                    status_callback(status_message)

                # Detect and handle duplicates
                if is_duplicate(file_path, processed_hashes, settings):
                    handle_duplicate(file_path, trash_dir, settings)
                    if log_callback:
                        log_callback(f"Duplicate moved to trash: {file_path}")
                    continue

                # Supported image formats including HEIC
                if ext.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.heic')):
                    # Process image
                    metadata = extract_image_metadata(file_path, settings)
                    if metadata is None:
                        logging.warning(f"Skipping file due to metadata extraction failure: {file_path}")
                        if log_callback:
                            log_callback(f"Skipping (metadata extraction failed): {file_path}")
                        continue
                    timestamp = metadata.get('timestamp')
                    gps_data = metadata.get('gps')
                    location_str, location_found = reverse_geocode(gps_data)

                    # Log based on geolocation result
                    if location_found:
                        logging.info(f"Location found: {location_str}")
                    else:
                        logging.warning(f"Location not found for GPS data in file: {file_path}")

                    new_file_path = rename_and_organize(file_path, timestamp, location_str, location_found, output_dir, settings)
                    if new_file_path:
                        logging.info(f"Image processed: {new_file_path}")
                        if log_callback:
                            log_callback(f"Image processed: {new_file_path}")

                elif ext.endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv')):
                    # Process video
                    new_file_path = process_video(file_path, output_dir, settings)
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

    except Exception as e:
        logging.error(f"Error organizing files: {e}")
        if log_callback:
            log_callback(f"Error organizing files: {e}")
