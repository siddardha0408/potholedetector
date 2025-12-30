import requests

# ADD THIS LINE HERE - It acts as the shared database for Cloud Sync
GLOBAL_POTHOLES = [] 

def get_live_context():
    try:
        ip_res = requests.get('http://ip-api.com/json/', timeout=5).json()
        lat, lon = ip_res.get('lat', 17.3850), ip_res.get('lon', 78.4867)
        geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {'User-Agent': 'RoadPulse_Pro_Auditor'}
        geo_data = requests.get(geo_url, headers=headers, timeout=5).json()
        
        address = geo_data.get('display_name', 'Locating...')
        short_addr = ", ".join(address.split(",")[:3])

        return {"lat": lat, "lon": lon, "address": short_addr}
    except:
        return {"lat": 17.3850, "lon": 78.4867, "address": "Hyderabad, Telangana"}