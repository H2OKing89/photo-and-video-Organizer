# modules/utils.py

import os
from PyQt6.QtCore import QStandardPaths
import pillow_heif  # Import pillow_heif to enable HEIC support in Pillow

# Register HEIC opener with Pillow
pillow_heif.register_heif_opener()

def get_default_pictures_folder():
    """
    Returns the default Pictures folder path for the current user using QStandardPaths.
    This method is more robust and cross-platform compatible.
    """
    paths = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.PicturesLocation)
    return paths[0] if paths else os.path.expanduser('~/Pictures')

def get_default_output_folder():
    """
    Returns the default Output folder path where organized media will be stored.
    """
    return os.path.join(get_default_pictures_folder(), "Organized")

def get_default_trash_folder():
    """
    Returns the default Trash folder path where duplicate files will be moved.
    """
    return os.path.join(get_default_pictures_folder(), 'Trash')
