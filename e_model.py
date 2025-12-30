import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

# 1. Load Data and Model
df = pd.read_csv('new_training_data.csv')
model = joblib.load('road_pulse_brain.pkl')

# Define features
X = df[['std', 'ptp', 'max']]
y = df['label']

# 2. Generate Confusion Matrix (Shows True vs False Detections)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Normal', 'Pothole'])
disp.plot(cmap='Blues')
plt.title('Confusion Matrix: Model Prediction Accuracy')
plt.savefig('confusion_matrix.png') # Saves a copy for your presentation
plt.show()

# 3. Feature Importance Plot (Shows which sensor data was most helpful)
importances = model.feature_importances_
feature_names = ['Std Deviation', 'Peak-to-Peak', 'Max G-Force']

plt.figure(figsize=(10, 5))
sns.barplot(x=importances, y=feature_names, palette='viridis')
plt.title('Feature Importance: Which sensor data matters most?')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.show()

print("✅ Performance graphs generated and saved as PNG files.")