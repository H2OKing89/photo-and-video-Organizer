# duplicate_detector.py

import os
import hashlib
import imagehash
from PIL import Image
import logging
import pillow_heif  # Ensure HEIC support is registered

# Register HEIC opener with Pillow for handling HEIC files
pillow_heif.register_heif_opener()

def compute_md5(file_path):
    """
    Computes the MD5 hash of a file.

    Parameters:
    - file_path (str): Path to the file.

    Returns:
    - str: MD5 hash hexadecimal string.
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logging.error(f"Error computing MD5 for {file_path}: {e}")
        return None

def compute_perceptual_hash(file_path):
    """
    Computes the perceptual hash of an image file.

    Parameters:
    - file_path (str): Path to the image file.

    Returns:
    - str: Perceptual hash string.
    """
    try:
        img = Image.open(file_path)
        phash = str(imagehash.phash(img))
        return phash
    except Exception as e:
        logging.error(f"Error computing perceptual hash for {file_path}: {e}")
        return None

def is_duplicate(file_path, processed_hashes, settings):
    """
    Determines if a file is a duplicate based on the selected hashing method.

    Parameters:
    - file_path (str): Path to the file.
    - processed_hashes (set): Set of previously computed hashes.
    - settings (dict): User-defined settings.

    Returns:
    - bool: True if duplicate, False otherwise.
    """
    duplicate_method = settings.get('duplicate_method', 'MD5 Hash')
    
    # Ensure that .heic files can be processed for hashing
    if file_path.lower().endswith('.heic'):
        logging.info(f"Processing duplicate detection for HEIC file: {file_path}")

    if duplicate_method == 'MD5 Hash':
        file_hash = compute_md5(file_path)
    elif duplicate_method == 'Perceptual Hash':
        file_hash = compute_perceptual_hash(file_path)
    else:
        file_hash = compute_md5(file_path)  # Default to MD5

    if file_hash is None:
        return False  # Unable to compute hash; treat as non-duplicate

    if file_hash in processed_hashes:
        return True
    else:
        processed_hashes.add(file_hash)
        return False

def handle_duplicate(file_path, trash_dir, settings):
    """
    Handles duplicate files by moving them to the trash directory.

    Parameters:
    - file_path (str): Path to the duplicate file.
    - trash_dir (str): Path to the trash directory.
    - settings (dict): User-defined settings.

    Returns:
    - None
    """
    try:
        os.makedirs(trash_dir, exist_ok=True)
        file_name = os.path.basename(file_path)
        destination = os.path.join(trash_dir, file_name)
        os.rename(file_path, destination)
        logging.info(f"Moved duplicate file {file_path} to {destination}")
    except Exception as e:
        logging.error(f"Error moving duplicate file {file_path} to trash: {e}")
