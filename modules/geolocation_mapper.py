# modules/geolocation_mapper.py

from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
import logging
import time
import json
import os
from pathlib import Path

# Load the Google Maps API key from environment variables or config
from dotenv import load_dotenv
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

if not GOOGLE_MAPS_API_KEY:
    logging.error("Google Maps API Key not found. Please set the GOOGLE_MAPS_API_KEY environment variable.")
    GOOGLE_MAPS_API_KEY = None  # Handle gracefully in reverse_geocode

# Initialize the geolocator with GoogleV3
geolocator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY, timeout=10)

# Define cache file path
CACHE_FILE = "geocode_cache.json"

# Load existing cache or initialize an empty dictionary
if Path(CACHE_FILE).is_file():
    with open(CACHE_FILE, 'r') as f:
        try:
            geocode_cache = json.load(f)
        except json.JSONDecodeError:
            geocode_cache = {}
            logging.warning("Geocode cache file is corrupted. Starting with an empty cache.")
else:
    geocode_cache = {}

def reverse_geocode(gps_data):
    """
    Converts GPS coordinates into a human-readable address.

    Returns:
    - tuple: (location_str, success_flag)
        - location_str (str): Human-readable location or "Unknown_Location"
        - success_flag (bool): True if geolocation was successful, False otherwise
    """
    try:
        if not gps_data:
            logging.warning("No GPS data provided.")
            return "Unknown_Location", False

        latitude = gps_data.get('latitude')
        longitude = gps_data.get('longitude')

        if latitude is None or longitude is None:
            logging.warning("Incomplete GPS data.")
            return "Unknown_Location", False

        # Create a unique key for caching based on coordinates rounded to 5 decimal places
        cache_key = f"{round(latitude, 5)},{round(longitude, 5)}"
        if cache_key in geocode_cache:
            logging.info(f"Geocode cache hit for coordinates: {cache_key}")
            return geocode_cache[cache_key], True

        if not GOOGLE_MAPS_API_KEY:
            logging.error("Google Maps API Key is not set. Cannot perform geocoding.")
            return "Unknown_Location", False

        # Implementing retry logic with a maximum of 3 attempts
        for attempt in range(3):
            try:
                location = geolocator.reverse(
                    (latitude, longitude),
                    exactly_one=True,
                    language='en'
                    # Removed 'addressdetails' as it's not supported by GoogleV3
                )
                if location and location.raw:
                    address = location.raw.get('address_components', [])
                    
                    # Extract relevant address components
                    city = None
                    state = None
                    country = None
                    street = None
                    poi = None
                    landmark = None

                    for component in address:
                        types = component.get('types', [])
                        if 'point_of_interest' in types or 'establishment' in types:
                            poi = component.get('long_name')
                        if 'neighborhood' in types or 'sublocality' in types:
                            landmark = component.get('long_name')
                        if 'locality' in types:
                            city = component.get('long_name')
                        if 'administrative_area_level_1' in types:
                            state = component.get('long_name')
                        if 'country' in types:
                            country = component.get('long_name')
                        if 'route' in types or 'street_number' in types:
                            street = component.get('long_name')

                    location_parts = []
                    if poi:
                        location_parts.append(poi.replace(" ", "_"))
                    elif landmark:
                        location_parts.append(landmark.replace(" ", "_"))

                    # Fallback to full address if no POI or landmark
                    if city and state and country:
                        location_parts.append(f"{city.replace(' ', '_')}_{state.replace(' ', '_')}_{country.replace(' ', '_')}")
                    elif country:
                        location_parts.append(country.replace(" ", "_"))
                    else:
                        location_parts.append("Unknown_Location")

                    location_str = "_".join(location_parts)

                    # Cache the result
                    geocode_cache[cache_key] = location_str
                    with open(CACHE_FILE, 'w') as f:
                        json.dump(geocode_cache, f, indent=2)

                    logging.info(f"Geocoding successful: {location_str} for coordinates {cache_key}")
                    return location_str, True
                else:
                    logging.warning("No address found for the given GPS coordinates.")
                    return "Unknown_Location", False
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logging.warning(f"Geocoding attempt {attempt + 1} failed: {e}")
                time.sleep(1)  # Wait before retrying

        logging.error("All geocoding attempts failed.")
        return "Unknown_Location", False
    except Exception as e:
        logging.error(f"Error in reverse_geocode: {e}")
        return "Unknown_Location", False
