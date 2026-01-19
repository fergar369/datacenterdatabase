"""
Geocoding functionality for location data
"""

from typing import Optional, Tuple, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import config


class Geocoder:
    """Handle geocoding operations"""

    def __init__(self):
        self.geolocator = Nominatim(
            user_agent=config.GEOCODING_USER_AGENT,
            timeout=config.GEOCODING_TIMEOUT
        )
        self.cache = {}

    def geocode_location(self, city: str = None, county: str = None,
                        state: str = None) -> Tuple[Optional[float], Optional[float], str]:
        """
        Geocode a location to latitude/longitude

        Args:
            city: City name
            county: County name
            state: State name

        Returns:
            (latitude, longitude, confidence_level)
        """

        # Build location string with available components
        location_parts = []

        if city:
            location_parts.append(city)
        if county:
            location_parts.append(f"{county} County")
        if state:
            location_parts.append(state)
        location_parts.append("USA")

        location_string = ", ".join(location_parts)

        # Check cache
        if location_string in self.cache:
            return self.cache[location_string]

        # Attempt geocoding
        try:
            time.sleep(1)  # Rate limiting
            location = self.geolocator.geocode(location_string)

            if location:
                lat, lon = location.latitude, location.longitude

                # Determine confidence
                if city:
                    confidence = "high"
                elif county:
                    confidence = "medium"
                else:
                    confidence = "low"

                result = (lat, lon, confidence)
                self.cache[location_string] = result
                return result

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"  Geocoding error for '{location_string}': {e}")

        # Fallback: return None
        result = (None, None, "failed")
        self.cache[location_string] = result
        return result

    def geocode_facility(self, facility: Dict) -> Dict:
        """
        Add geocoding to a facility dict

        Args:
            facility: Facility dictionary

        Returns:
            Updated facility dictionary with lat/lon
        """

        lat, lon, confidence = self.geocode_location(
            city=facility.get('location_city'),
            county=facility.get('location_county'),
            state=facility.get('location_state')
        )

        facility['latitude'] = lat
        facility['longitude'] = lon
        facility['geocoding_confidence'] = confidence

        return facility


# Manual coordinates for common locations (to speed up processing)
COUNTY_CENTROIDS = {
    # Texas counties
    ("Travis", "TX"): (30.2672, -97.7431),
    ("Travis", "Texas"): (30.2672, -97.7431),
    ("Dallas", "TX"): (32.7767, -96.7970),
    ("Dallas", "Texas"): (32.7767, -96.7970),
    ("Harris", "TX"): (29.7604, -95.3698),
    ("Harris", "Texas"): (29.7604, -95.3698),
    ("Collin", "TX"): (33.1972, -96.5731),
    ("Collin", "Texas"): (33.1972, -96.5731),
    ("Bexar", "TX"): (29.4241, -98.4936),
    ("Bexar", "Texas"): (29.4241, -98.4936),
    ("Williamson", "TX"): (30.6280, -97.6789),
    ("Williamson", "Texas"): (30.6280, -97.6789),
    ("Denton", "TX"): (33.2148, -97.1331),
    ("Denton", "Texas"): (33.2148, -97.1331),
    ("Fort Bend", "TX"): (29.5693, -95.7705),
    ("Fort Bend", "Texas"): (29.5693, -95.7705),
    ("Tarrant", "TX"): (32.7554, -97.3308),
    ("Tarrant", "Texas"): (32.7554, -97.3308),

    # Virginia counties (Loudoun - major DC hub)
    ("Loudoun", "VA"): (39.0437, -77.5647),
    ("Loudoun", "Virginia"): (39.0437, -77.5647),
    ("Prince William", "VA"): (38.7293, -77.4730),
    ("Prince William", "Virginia"): (38.7293, -77.4730),
    ("Fairfax", "VA"): (38.8462, -77.3064),
    ("Fairfax", "Virginia"): (38.8462, -77.3064),

    # Ohio counties
    ("Franklin", "OH"): (39.9612, -82.9988),
    ("Franklin", "Ohio"): (39.9612, -82.9988),

    # Pennsylvania counties
    ("Allegheny", "PA"): (40.4406, -79.9959),
    ("Allegheny", "Pennsylvania"): (40.4406, -79.9959),

    # Other major states
    ("Maricopa", "AZ"): (33.4484, -112.0740),
    ("Maricopa", "Arizona"): (33.4484, -112.0740),
    ("Fulton", "GA"): (33.7490, -84.3880),
    ("Fulton", "Georgia"): (33.7490, -84.3880),
    ("King", "WA"): (47.6062, -122.3321),
    ("King", "Washington"): (47.6062, -122.3321),
}


def get_county_centroid(county: str, state: str) -> Tuple[Optional[float], Optional[float]]:
    """Get pre-defined county centroid if available"""
    key = (county, state)
    if key in COUNTY_CENTROIDS:
        lat, lon = COUNTY_CENTROIDS[key]
        return lat, lon
    return None, None
