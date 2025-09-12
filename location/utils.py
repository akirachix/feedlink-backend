import requests
from django.conf import settings

def geocode_address(address: str):
    try:
        token = settings.LOCATION_TOKEN
        base_url = settings.LOCATIONIQ_BASE_URL
        url=f"{base_url}{token}&q={address}&format=json"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except Exception as e:
        print(f"Geocoding failed for '{address}': {e}")
    return 0.0, 0.0