from flask import Flask, render_template, jsonify, request
import joblib, numpy as np, sqlite3, json, os
from api_helper import get_live_context

app = Flask(__name__)

# Load AI Model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'road_pulse_brain.pkl')
try:
    model = joblib.load(model_path)
except:
    model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/audit', methods=['POST'])
def audit():
    data = request.json
    vibs = data.get('vibrations', [])
    m_lat = data.get('manualLat') # Receives searched Latitude
    m_lon = data.get('manualLon') # Receives searched Longitude
    
    mag = np.array(vibs) if len(vibs) > 0 else np.zeros(50)
    
    # Feature Extraction
    std_dev = float(np.std(mag))
    max_g = float(np.max(mag))
    ptp = float(np.max(mag) - np.min(mag)) 
    
    status = 0
    if model and len(vibs) >= 10:
        try:
            status = int(model.predict([[std_dev, ptp, max_g]])[0])
        except: status = 0

    # Calibration Override (Guarantees trigger for demo)
    if max_g > 14.0 or ptp > 17.0:
        status = 2

    # Speed Bump Filter
    if status == 2 and (std_dev / (ptp + 0.1)) < 0.12:
        status = 0
            
    info = get_live_context()
    
    # Use Searched location if provided, otherwise use real GPS/IP
    final_lat = m_lat if m_lat is not None else info['lat']
    final_lon = m_lon if m_lon is not None else info['lon']

    conn = sqlite3.connect('roadpulse.db')
    c = conn.cursor()

    if status == 2:
        # Check for duplicates at the target location
        c.execute("SELECT id FROM potholes WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?", 
                  (final_lat-0.0001, final_lat+0.0001, final_lon-0.0001, final_lon+0.0001))
        if not c.fetchone():
            snippet_json = json.dumps(mag.tolist()) 
            c.execute("INSERT INTO potholes (lat, lon, address, std, ptp, max_g, snippet) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (final_lat, final_lon, info['address'], std_dev, ptp, max_g, snippet_json))
            conn.commit()

    # Retrieve markers
    c.execute("SELECT lat, lon, address, std, ptp, max_g, snippet FROM potholes")
    global_markers = []
    for r in c.fetchall():
        try: 
            snip = json.loads(r[6])
        except: 
            snip = []
        global_markers.append({
            "lat": r[0], "lon": r[1], "addr": r[2], 
            "std": round(r[3], 3), "ptp": round(r[4], 3), 
            "max": round(r[5], 3), "snippet": snip
        })
    conn.close()

    return jsonify({
        "status": status,
        "lat": info['lat'], "lon": info['lon'],
        "address": info['address'],
        "vibrations": mag.tolist()[-50:],
        "global_markers": global_markers,
        "metrics": {"std": round(std_dev, 3), "ptp": round(ptp, 3), "max": round(max_g, 3)}
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8888))
    app.run(host='0.0.0.0', port=port)
