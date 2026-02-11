from geopy.geocoders import Nominatim
def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location.address
print(get_location_name(41.539331634890786, 60.622422405764574))
