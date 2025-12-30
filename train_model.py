import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load Training Data
# Ensure you have 'new_training_data.csv' generated from your collection script
df = pd.read_csv('new_training_data.csv')

# 2. Train
X = df[['std', 'ptp', 'max']]
y = df['label'] # 0 for Smooth, 2 for Pothole

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# 3. Save
joblib.dump(model, 'road_pulse_brain.pkl')
print("✅ New Brain File Saved!")