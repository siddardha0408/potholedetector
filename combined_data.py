import pandas as pd
import os

# Define the files you KNOW you have
files_to_combine = ['trip1_sensors.csv'] # Add others if you have them, e.g., 'trip2.csv'

combined_data = []

print("Checking for files...")
for f in files_to_combine:
    if os.path.exists(f):
        print(f"✅ Found {f}, reading it...")
        df = pd.read_csv(f)
        combined_data.append(df)
    else:
        print(f"❌ Could not find {f}")

if combined_data:
    master_df = pd.concat(combined_data, ignore_index=True)
    # This creates the file in the current folder
    master_df.to_csv('combined_sensor_data.csv', index=False)
    print("\n🎉 SUCCESS! 'combined_sensor_data.csv' has been created.")
    print(f"Total rows in new file: {len(master_df)}")
else:
    print("\n🛑 ERROR: No data was combined. Check your file names!")