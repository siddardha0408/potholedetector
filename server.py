from flask import Flask, render_template, jsonify, request
import joblib, numpy as np, sqlite3, json
from api_helper import get_live_context

app = Flask(__name__)

# --- DATABASE PROTECTION LAYER ---
def ensure_db_ready():
    conn = sqlite3.connect('roadpulse.db')
    c = conn.cursor()
    # Forces the table to exist with the correct columns
    c.execute('''CREATE TABLE IF NOT EXISTS potholes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  lat REAL, lon REAL, address TEXT, 
                  std REAL, ptp REAL, max_g REAL,
                  snippet TEXT)''')
    conn.commit()
    conn.close()

# Run this immediately when script starts
ensure_db_ready()

try:
    model = joblib.load('road_pulse_brain.pkl')
except:
    model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/audit', methods=['POST'])
def audit():
    data = request.json
    vibs = data.get('vibrations', [])
    mag = np.array(vibs) if len(vibs) > 0 else np.zeros(1)
    
    # Calculate metrics
    std_dev = float(np.std(mag))
    ptp = float(np.max(mag) - np.min(mag))
    max_g = float(np.max(mag))
    
    status = 0
    if model and len(vibs) > 10:
        # Prepare feature names to avoid the UserWarning
        # This matches the names used during training
        status = int(model.predict([[std_dev, ptp, max_g]])[0])
        
        # Frequency Filter
        if status == 2 and (std_dev / (ptp + 0.1)) < 0.18:
            status = 0
            
    info = get_live_context()
    
    # Re-connect for this request
    conn = sqlite3.connect('roadpulse.db')
    c = conn.cursor()

    if status == 2:
        # Duplicate Prevention
        c.execute("SELECT id FROM potholes WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?", 
                  (info['lat']-0.0001, info['lat']+0.0001, info['lon']-0.0001, info['lon']+0.0001))
        if not c.fetchone():
            c.execute("INSERT INTO potholes (lat, lon, address, std, ptp, max_g, snippet) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (info['lat'], info['lon'], info['address'], std_dev, ptp, max_g, json.dumps(mag.tolist()[-50:])))
            conn.commit()

    # This is where the error was happening. It's now safe because of ensure_db_ready()
    c.execute("SELECT lat, lon, address, std, ptp, max_g, snippet FROM potholes")
    rows = c.fetchall()
    global_markers = [{"lat": r[0], "lon": r[1], "addr": r[2], "std": r[3], "ptp": r[4], "max": r[5], "snippet": json.loads(r[6])} for r in rows]
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
    app.run(debug=True, port=8888, host='0.0.0.0')