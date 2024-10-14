"""
main.py

Entry point for the Photo Organizer program. It orchestrates the workflow by
utilizing functions from various modules to extract metadata, detect duplicates,
organize files, and handle videos.

Usage:
    python main.py --input_dir "C:\\Path\\To\\input_media" --output_dir "C:\\Path\\To\\output_media" --trash_dir "C:\\Path\\To\\trash_duplicates"
"""

import os
import argparse
from tqdm import tqdm
from modules.logger import setup_logging
from modules.duplicate_detector import is_duplicate, handle_duplicate
from modules.metadata_extractor import extract_image_metadata
from modules.geolocation_mapper import reverse_geocode
from modules.file_organizer import rename_and_organize
from modules.video_handler import process_video
import logging

def main(input_dir, output_dir, trash_dir):
    """
    Main function that orchestrates the media organization process.

    Parameters:
    - input_dir (str): Path to the input media directory.
    - output_dir (str): Path to the output directory where organized media will be stored.
    - trash_dir (str): Path to the trash directory where duplicates will be moved.

    Returns:
    - None
    """
    setup_logging(os.path.join('logs', 'photo_organizer.log'))
    logging.info(f"Starting organization: Input - {input_dir}, Output - {output_dir}, Trash - {trash_dir}")
    
    processed_hashes = set()

    # Ensure output directories exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(trash_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for file in tqdm(files, desc="Processing files"):
            file_path = os.path.join(root, file)
            ext = file.lower()

            # Detect and handle duplicates
            if is_duplicate(file_path, processed_hashes):
                handle_duplicate(file_path, trash_dir)
                continue

            if ext.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                # Process image
                metadata = extract_image_metadata(file_path)
                if metadata is None:
                    logging.warning(f"Skipping file due to metadata extraction failure: {file_path}")
                    continue
                timestamp = metadata.get('timestamp')
                gps_data = metadata.get('gps')
                location = reverse_geocode(gps_data)

                new_file_path = rename_and_organize(file_path, timestamp, location, output_dir)
                if new_file_path:
                    logging.info(f"Image processed: {new_file_path}")

            elif ext.endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv')):
                # Process video
                new_file_path = process_video(file_path, output_dir)
                if new_file_path:
                    logging.info(f"Video processed: {new_file_path}")

            else:
                logging.warning(f"Unsupported file format: {file_path}")
                continue

    logging.info("Organization completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize photos and videos based on metadata.")
    parser.add_argument('--input_dir', type=str, required=True, help="Path to the input media directory")
    parser.add_argument('--output_dir', type=str, required=True, help="Path to the output directory")
    parser.add_argument('--trash_dir', type=str, required=True, help="Path to the trash directory for duplicates")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.trash_dir)
