from geopy.geocoders import Nominatim


def geocode_location(location):
    geolocator = Nominatim(user_agent="onemap")
    location = geolocator.geocode(location)
    return location.latitude, location.longitude

