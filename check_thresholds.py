import pandas as pd
import time

# Collect 20 samples of "Potholes" and 20 samples of "Normal"
def collect_samples(label, num_samples=20):
    print(f"--- STARTING COLLECTION FOR LABEL: {label} ---")
    data = []
    for i in range(num_samples):
        # In a real demo, you would pull these from your dashboard logs
        # For training, manually input your current 'Max G' and 'Std Dev'
        print(f"Sample {i+1}: Shake/Move phone now...")
        time.sleep(1)
        # Placeholder for your real-time values observed on dashboard
        std = float(input("Enter Std Dev seen on screen: "))
        ptp = float(input("Enter Peak-to-Peak seen on screen: "))
        max_v = float(input("Enter Max G seen on screen: "))
        data.append([std, ptp, max_v, label])
    
    return data

# Label 0 = Normal, Label 2 = Pothole
new_data = collect_samples(0) + collect_samples(2)
df = pd.DataFrame(new_data, columns=['std', 'ptp', 'max', 'label'])
df.to_csv('new_training_data.csv', index=False)
print("Data saved. Now run the trainer script.")