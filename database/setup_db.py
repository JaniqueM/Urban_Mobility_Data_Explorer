import sqlite3
import pandas as pd

# Load CSV
df = pd.read_csv("train.csv")

# Convert datetime columns (adjust names if needed)
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

# Create required fields
df['duration_minutes'] = (
    (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60
)

df['pickup_hour'] = df['pickup_datetime'].dt.hour
df['day_of_week'] = df['pickup_datetime'].dt.dayofweek

# Avoid division by zero
df = df[df['duration_minutes'] > 0]

# If trip_distance exists
if 'trip_distance' in df.columns:
    df['speed_kmh'] = df['trip_distance'] / (df['duration_minutes'] / 60)
else:
    df['speed_kmh'] = 0  # fallback if missing

# Connect to SQLite
conn = sqlite3.connect("taxi.db")

# Save table
df.to_sql("trips", conn, if_exists="replace", index=False)

print("Database created successfully with trips table!")

conn.close()