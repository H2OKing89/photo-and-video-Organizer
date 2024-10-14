"""
geolocation_mapper.py

This module converts GPS coordinates extracted from media files into
human-readable location names using reverse geocoding.

Functions:
- reverse_geocode(gps_data): Converts GPS data into a location string.
- get_decimal_from_dms(dms, ref): Converts DMS (Degrees, Minutes, Seconds) to decimal format.
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import logging
import time

# Initialize the geolocator with a user agent
geolocator = Nominatim(user_agent="photo_organizer")

def reverse_geocode(gps_data, cache={}):
    """
    Converts GPS data into a human-readable address using reverse geocoding.

    Parameters:
    - gps_data (dict): Dictionary containing 'GPSLatitude', 'GPSLatitudeRef',
                       'GPSLongitude', and 'GPSLongitudeRef'.
    - cache (dict): A cache to store previously reverse geocoded locations.

    Returns:
    - str or None: The address as a string if successful, else None.
    """
    if not gps_data:
        return None
    lat = get_decimal_from_dms(gps_data.get('GPSLatitude'), gps_data.get('GPSLatitudeRef'))
    lon = get_decimal_from_dms(gps_data.get('GPSLongitude'), gps_data.get('GPSLongitudeRef'))
    if lat is not None and lon is not None:
        # Check if location is already in cache
        if (lat, lon) in cache:
            return cache[(lat, lon)]
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True)
            if location:
                address = location.address
                cache[(lat, lon)] = address
                time.sleep(1)  # To respect Nominatim's usage policy
                return address
        except GeopyError as e:
            logging.error(f"Geocoding error for coordinates ({lat}, {lon}): {e}")
    return None

def get_decimal_from_dms(dms, ref):
    """
    Converts GPS coordinates from DMS (Degrees, Minutes, Seconds) format to decimal degrees.

    Parameters:
    - dms (tuple): Tuple containing degrees, minutes, and seconds.
    - ref (str): Hemisphere reference ('N', 'S', 'E', 'W').

    Returns:
    - float or None: Decimal degrees representation or None if invalid input.
    """
    if dms and ref:
        def to_float(rational):
            try:
                return float(rational.num) / float(rational.den)
            except AttributeError:
                # If it's not an IFDRational, assume it's a float or a tuple
                if isinstance(rational, tuple) and len(rational) == 2:
                    return rational[0] / rational[1]
                else:
                    return float(rational)
        
        degrees = to_float(dms[0])
        minutes = to_float(dms[1])
        seconds = to_float(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        if ref in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    
    return None
