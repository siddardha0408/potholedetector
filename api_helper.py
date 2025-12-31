import requests
import sqlite3

def init_db():
    conn = sqlite3.connect('roadpulse.db')
    c = conn.cursor()
    # Ensure all columns exist, especially 'snippet' for the replay
    c.execute('''CREATE TABLE IF NOT EXISTS potholes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  lat REAL, lon REAL, address TEXT, 
                  std REAL, ptp REAL, max_g REAL,
                  snippet TEXT)''')
    conn.commit()
    conn.close()

def get_live_context():
    try:
        # IP-based location for high accuracy during demo
        ip_res = requests.get('https://ipapi.co/json/', timeout=5).json()
        lat, lon = ip_res.get('latitude', 17.3850), ip_res.get('longitude', 78.4867)
        
        geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {'User-Agent': 'RoadPulse_Audit_System'}
        geo_data = requests.get(geo_url, headers=headers, timeout=5).json()
        
        address = geo_data.get('display_name', 'Unknown Location')
        short_addr = ", ".join(address.split(",")[:3])
        return {"lat": lat, "lon": lon, "address": short_addr}
    except:
        return {"lat": 17.3850, "lon": 78.4867, "address": "Hyderabad, Telangana"}

init_db()
