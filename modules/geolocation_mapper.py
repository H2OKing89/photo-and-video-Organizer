# modules/geolocation_mapper.py

"""
geolocation_mapper.py

This module handles the conversion of GPS coordinates into human-readable locations.
It utilizes the geopy library to perform reverse geocoding.
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
import logging
import time

def _convert_to_degrees(value, ref):
    """
    Converts GPS coordinates stored in EXIF to degrees in float format.

    Parameters:
    - value (tuple): Tuple containing degrees, minutes, and seconds as IFDRational objects.
    - ref (str): Reference direction ('N', 'S', 'E', 'W').

    Returns:
    - float: Converted degrees.
    """
    try:
        d, m, s = value
        degrees = float(d) + float(m) / 60.0 + float(s) / 3600.0
        if ref in ['S', 'W']:
            degrees = -degrees
        return degrees
    except Exception as e:
        logging.error(f"Error converting GPS coordinates: {e}")
        return 0.0

# Initialize the geolocator with a user agent and increased timeout
geolocator = Nominatim(user_agent="photo_video_organizer", timeout=10)

def reverse_geocode(gps_data):
    """
    Converts GPS coordinates into a human-readable address.

    Parameters:
    - gps_data (dict): Dictionary containing 'GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef'.

    Returns:
    - str: The name of the location (e.g., city or landmark).
    """
    try:
        if not gps_data:
            logging.warning("No GPS data provided.")
            return "Unknown_Location"

        latitude = _convert_to_degrees(gps_data.get('GPSLatitude'), gps_data.get('GPSLatitudeRef'))
        longitude = _convert_to_degrees(gps_data.get('GPSLongitude'), gps_data.get('GPSLongitudeRef'))

        if latitude == 0.0 and longitude == 0.0:
            logging.warning("Invalid GPS coordinates: (0.0, 0.0)")
            return "Unknown_Location"

        # Implementing retry logic with a maximum of 3 attempts
        for attempt in range(3):
            try:
                location = geolocator.reverse(
                    (latitude, longitude),
                    exactly_one=True,
                    language='en',
                    addressdetails=1
                )
                if location and location.address:
                    address = location.raw.get('address', {})
                    city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
                    country = address.get('country')
                    poi = address.get('attraction') or address.get('tourism') or address.get('amenity')  # Point of Interest
                    landmark = address.get('road') or address.get('neighbourhood') or address.get('suburb')  # Landmark

                    location_parts = []
                    if poi:
                        location_parts.append(poi.replace(" ", "_"))
                    elif landmark:
                        location_parts.append(landmark.replace(" ", "_"))

                    if city and country:
                        location_parts.append(f"{city.replace(' ', '_')}_{country.replace(' ', '_')}")
                    elif country:
                        location_parts.append(country.replace(" ", "_"))
                    else:
                        location_parts.append("Unknown_Location")

                    location_str = "_".join(location_parts)
                    return location_str
                else:
                    logging.warning("No address found for the given GPS coordinates.")
                    return "Unknown_Location"
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logging.warning(f"Geocoding attempt {attempt + 1} failed: {e}")
                time.sleep(1)  # Wait before retrying

        logging.error("All geocoding attempts failed.")
        return "Unknown_Location"

    except Exception as e:
        logging.error(f"Error in reverse_geocode: {e}")
        return "Unknown_Location"
