"""
duplicate_detector.py

This module handles the detection and management of duplicate media files.
It uses hashing to identify duplicates and moves them to a designated trash directory.

Functions:
- get_file_hash(file_path): Generates an MD5 hash for a file.
- is_duplicate(file_path, processed_hashes): Checks if a file is a duplicate.
- handle_duplicate(file_path, trash_dir): Moves duplicate files to the trash directory.
"""

import hashlib
import logging
import shutil
import os

def get_file_hash(file_path):
    """
    Generates an MD5 hash for the given file.

    Parameters:
    - file_path (str): Path to the file.

    Returns:
    - str or None: The MD5 hash as a hexadecimal string, or None if an error occurs.
    """
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as file:
            buffer = file.read(65536)  # Read in 64KB chunks
            while buffer:
                hasher.update(buffer)
                buffer = file.read(65536)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing file {file_path}: {e}")
        return None

def is_duplicate(file_path, processed_hashes):
    """
    Checks if the given file is a duplicate based on its hash.

    Parameters:
    - file_path (str): Path to the file.
    - processed_hashes (set): Set of hashes of already processed files.

    Returns:
    - bool: True if duplicate, False otherwise.
    """
    file_hash = get_file_hash(file_path)
    if file_hash is None:
        return False
    if file_hash in processed_hashes:
        return True
    else:
        processed_hashes.add(file_hash)
        return False

def handle_duplicate(file_path, trash_dir):
    """
    Moves the duplicate file to the trash directory.

    Parameters:
    - file_path (str): Path to the duplicate file.
    - trash_dir (str): Path to the trash directory.

    Returns:
    - None
    """
    try:
        os.makedirs(trash_dir, exist_ok=True)
        destination = os.path.join(trash_dir, os.path.basename(file_path))
        shutil.move(file_path, destination)
        logging.info(f"Duplicate moved to trash: {file_path} -> {destination}")
    except Exception as e:
        logging.error(f"Error moving duplicate {file_path} to trash: {e}")
