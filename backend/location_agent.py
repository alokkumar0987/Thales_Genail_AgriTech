# location_agent.py
import requests
from typing import Dict, Optional, Tuple
from geopy.geocoders import Nominatim
from langchain.tools import tool
import re

class LocationAgent:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="agricultural_advisor")
        self.current_location = None
        self.current_coordinates = None
    
    def get_location_from_ip(self) -> Optional[Dict[str, str]]:
        """
        Automatically detect user's location based on IP address using ipinfo.io
        
        Returns:
            Dictionary with location details or None if detection fails
        """
        try:
            ip = requests.get('https://api.ipify.org').text
            resp = requests.get(f'https://ipinfo.io/{ip}/json').json()
            loc = resp.get('loc')  # "lat,lng"
            city = resp.get('city')
            state = resp.get('region')
            country = resp.get('country')
            
            if loc:
                lat, lng = loc.split(',')
                location_data = {
                    'city': city,
                    'state': state,
                    'country': country,
                    'lat': lat,
                    'lng': lng,
                    'source': 'ipinfo'
                }
                
                # Update current location
                self.current_location = self.format_location_string(location_data)
                self.current_coordinates = (float(lat), float(lng))
                
                return location_data
        except Exception as e:
            print(f"Location detection error: {e}")
        
        return None

    def get_location_from_coordinates(self, lat: float, lng: float) -> Optional[Dict[str, str]]:
        """
        Get location details from coordinates
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Dictionary with location details
        """
        try:
            location = self.geolocator.reverse((lat, lng), exactly_one=True)
            if location:
                address = location.raw.get('address', {})
                location_data = {
                    'city': address.get('city') or address.get('town') or address.get('village'),
                    'state': address.get('state'),
                    'country': address.get('country'),
                    'lat': lat,
                    'lng': lng,
                    'source': 'coordinates'
                }
                
                # Update current location
                self.current_location = self.format_location_string(location_data)
                self.current_coordinates = (lat, lng)
                
                return location_data
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
        return None

    def format_location_string(self, location_data: Dict[str, str]) -> str:
        """
        Format location data into a readable string
        
        Args:
            location_data: Dictionary with location details
            
        Returns:
            Formatted location string
        """
        parts = []
        if location_data.get('city'):
            parts.append(location_data['city'])
        if location_data.get('state'):
            parts.append(location_data['state'])
        if location_data.get('country'):
            parts.append(location_data['country'])
        return ', '.join(parts) if parts else "Unknown location"
    
    def get_location_info(self, query: str = None) -> str:
        """
        Get comprehensive location information based on query
        
        Args:
            query: Optional location query
            
        Returns:
            Formatted location information
        """
        # If a specific location is mentioned in the query, try to geocode it
        if query:
            # Extract potential location names from query
            location_queries = self.extract_location_from_query(query)
            
            for loc_query in location_queries:
                try:
                    location = self.geolocator.geocode(loc_query)
                    if location:
                        location_data = self.get_location_from_coordinates(
                            location.latitude, location.longitude
                        )
                        if location_data:
                            location_str = self.format_location_string(location_data)
                            return f"📍 Location: {location_str}\n🌐 Coordinates: {location.latitude}, {location.longitude}"
                except Exception as e:
                    print(f"Error geocoding {loc_query}: {e}")
        
        # If no specific location in query or geocoding failed, use current location
        if self.current_location:
            lat, lng = self.current_coordinates
            return f"📍 Your current location: {self.current_location}\n🌐 Coordinates: {lat}, {lng}"
        else:
            # Try to detect location from IP
            location_data = self.get_location_from_ip()
            if location_data:
                location_str = self.format_location_string(location_data)
                lat, lng = self.current_coordinates
                return f"📍 Detected location: {location_str}\n🌐 Coordinates: {lat}, {lng}"
            else:
                return "❌ Could not detect your location. Please provide your location manually."
    
    def extract_location_from_query(self, query: str) -> list:
        """
        Extract potential location names from a query
        
        Args:
            query: User query text
            
        Returns:
            List of potential location names
        """
        # Common location indicators
        location_indicators = [
            "in", "at", "near", "around", "close to", 
            "location", "place", "area", "region"
        ]
        
        # Extract words that might be location names
        words = query.split()
        potential_locations = []
        
        for i, word in enumerate(words):
            # If word is a location indicator, take the next few words
            if word.lower() in location_indicators and i + 1 < len(words):
                # Take up to 3 words after the indicator
                location = " ".join(words[i+1:min(i+4, len(words))])
                potential_locations.append(location)
            
            # Also check for standalone location names (capitalized words)
            if word.istitle() and len(word) > 2:
                potential_locations.append(word)
        
        return potential_locations
    
    def set_location(self, location_query: str) -> str:
        """
        Set a manual location for the user
        
        Args:
            location_query: Location description (e.g., "Punjab, India")
            
        Returns:
            Confirmation message with location details
        """
        try:
            location = self.geolocator.geocode(location_query)
            if location:
                location_data = self.get_location_from_coordinates(
                    location.latitude, location.longitude
                )
                if location_data:
                    location_str = self.format_location_string(location_data)
                    return f"✅ Location set to: {location_str}\n🌐 Coordinates: {location.latitude}, {location.longitude}"
            
            return f"❌ Could not find details for location: {location_query}. Using as provided."
        except Exception as e:
            return f"❌ Error setting manual location: {str(e)}"

# Create a global instance
location_agent = LocationAgent()

# Tool functions for LangChain compatibility
@tool
def detect_user_location() -> str:
    """
    Detect the user's location automatically
    
    Returns:
        Location detection result
    """
    return location_agent.get_location_info()

@tool
def set_manual_location(location_query: str) -> str:
    """
    Set a manual location for the user
    
    Args:
        location_query: Location description (e.g., "Punjab, India")
        
    Returns:
        Confirmation message with location details
    """
    return location_agent.set_location(location_query)

@tool
def get_location_info(query: str = None) -> str:
    """
    Get comprehensive location information
    
    Args:
        query: Optional location query
        
    Returns:
        Formatted location information
    """
    return location_agent.get_location_info(query)

@tool
def detect_user_location_json() -> dict:
    """
    Detect the user's location automatically and return a structured JSON.
    """
    info_str = location_agent.get_location_info()
    
    import re
    match = re.search(r"Coordinates: ([\d\.\-]+), ([\d\.\-]+)", info_str)
    lat, lng = (float(match[1]), float(match[2])) if match else (None, None)
    
    return {
        "success": True if lat is not None and lng is not None else False,
        "location": location_agent.current_location or "Unknown",
        "latitude": lat,
        "longitude": lng,
        "source": getattr(location_agent, "current_coordinates", None) and "ipinfo" or None
    }
