import pandas as pd
import numpy as np
import os

def get_clean_df(filepath):
    print("Loading dataset...")
    df = pd.read_csv(filepath)
    original_count = len(df)
    print(f"Original records: {original_count}")

    # --- Drop duplicates ---
    df.drop_duplicates(inplace=True)

    # --- Parse timestamps ---
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')

    # --- Drop rows with null timestamps or coordinates ---
    df.dropna(subset=[
        'pickup_datetime', 'dropoff_datetime',
        'pickup_longitude', 'pickup_latitude',
        'dropoff_longitude', 'dropoff_latitude'
    ], inplace=True)

    # --- Filter valid NYC coordinates ---
    df = df[
        (df['pickup_longitude'].between(-74.25, -73.70)) &
        (df['pickup_latitude'].between(40.49, 40.92)) &
        (df['dropoff_longitude'].between(-74.25, -73.70)) &
        (df['dropoff_latitude'].between(40.49, 40.92))
    ]

    # --- Filter valid trip durations (1 min to 2 hrs) ---
    df = df[(df['trip_duration'] > 60) & (df['trip_duration'] < 7200)]

    # --- Filter valid passenger count ---
    df = df[(df['passenger_count'] > 0) & (df['passenger_count'] <= 6)]

    # --- Derived features ---
    # 1. Speed in km/h
    df['trip_distance_km'] = df['trip_duration'] / 3600 * 30  # estimated
    df['speed_kmh'] = df['trip_distance_km'] / (df['trip_duration'] / 3600)

    # 2. Pickup hour
    df['pickup_hour'] = df['pickup_datetime'].dt.hour

    # 3. Day of week (0=Monday, 6=Sunday)
    df['day_of_week'] = df['pickup_datetime'].dt.dayofweek

    # 4. Trip duration in minutes
    df['duration_minutes'] = df['trip_duration'] / 60

    # --- Log excluded records ---
    excluded = original_count - len(df)
    print(f"Excluded records: {excluded}")
    print(f"Clean records remaining: {len(df)}")

    return df


if __name__ == "__main__":
    # Test the cleaning pipeline
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'Data', 'train.csv')
    df = get_clean_df(data_path)
    print(df.head())
    print(df.columns.tolist())