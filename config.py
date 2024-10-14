# config.py

"""
config.py

Configuration settings module for the Photo and Video Organizer program. It allows for
easy adjustments of parameters without modifying the core code. Settings can be loaded
from or saved to a configuration file or managed using QSettings within the GUI.

Functions:
- load_settings(): Loads settings from QSettings.
- save_settings(settings): Saves settings to QSettings.
"""

from PyQt6.QtCore import QSettings
import os

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
        'naming_convention': settings.value('naming_convention', 'Date_Location')
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
    config_settings.setValue('naming_convention', settings_dict.get('naming_convention', 'Date_Location'))
