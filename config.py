# config.py

from PyQt6.QtCore import QSettings
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

def load_settings():
    """
    Loads settings from QSettings. If not set, default to the user's Pictures directory.

    Returns:
    - dict: Dictionary containing configuration settings, including directories and preferences.
    """
    settings = QSettings("YourCompany", "PhotoOrganizer")

    # Default to the user's Pictures directory for first-time setup
    default_pictures_dir = os.path.expanduser('~/Pictures')

    config = {
        'input_dir': settings.value('input_dir', default_pictures_dir),
        'output_dir': settings.value('output_dir', os.path.join(default_pictures_dir, "Organized")),
        'trash_dir': settings.value('trash_dir', os.path.join(default_pictures_dir, 'Trash')),
        'duplicate_method': settings.value('duplicate_method', 'MD5 Hash'),
        'include_jpg': settings.value('include_jpg', True, type=bool),
        'include_png': settings.value('include_png', True, type=bool),
        'include_mp4': settings.value('include_mp4', True, type=bool),
        'include_mov': settings.value('include_mov', True, type=bool),
        'include_heic': settings.value('include_heic', False, type=bool),
        'naming_convention': settings.value('naming_convention', 'Date_Location'),
        'google_maps_api_key': os.getenv('GOOGLE_MAPS_API_KEY')  # Add API key to config
    }
    return config

def save_settings(settings_dict):
    """
    Saves the current settings to QSettings.

    Parameters:
    - settings_dict (dict): Dictionary containing configuration settings.

    Returns:
    - None
    """
    config_settings = QSettings("YourCompany", "PhotoOrganizer")
    config_settings.setValue('input_dir', settings_dict.get('input_dir', os.path.expanduser('~/Pictures')))
    config_settings.setValue('output_dir', settings_dict.get('output_dir', os.path.join(os.path.expanduser('~/Pictures'), "Organized")))
    config_settings.setValue('trash_dir', settings_dict.get('trash_dir', os.path.join(os.path.expanduser('~/Pictures'), 'Trash')))
    config_settings.setValue('duplicate_method', settings_dict.get('duplicate_method', 'MD5 Hash'))
    config_settings.setValue('include_jpg', settings_dict.get('include_jpg', True))
    config_settings.setValue('include_png', settings_dict.get('include_png', True))
    config_settings.setValue('include_mp4', settings_dict.get('include_mp4', True))
    config_settings.setValue('include_mov', settings_dict.get('include_mov', True))
    config_settings.setValue('include_heic', settings_dict.get('include_heic', False))
    config_settings.setValue('naming_convention', settings_dict.get('naming_convention', 'Date_Location'))
