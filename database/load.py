import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clean import get_clean_df
from db_init import get_connection, init_db, DB_PATH

def load_data():
    # Step 1: Initialize the database
    print("Initializing database...")
    init_db()

    # Step 2: Load and clean the data
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'train.csv')
    df = get_clean_df(data_path)

    # Step 3: Keep only the columns we need
    columns = [
        'id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime',
        'passenger_count', 'pickup_longitude', 'pickup_latitude',
        'dropoff_longitude', 'dropoff_latitude', 'store_and_fwd_flag',
        'trip_duration', 'trip_distance_km', 'speed_kmh',
        'pickup_hour', 'day_of_week', 'duration_minutes'
    ]
    df = df[columns]

    # Step 4: Convert datetimes to strings for SQLite
    df['pickup_datetime'] = df['pickup_datetime'].astype(str)
    df['dropoff_datetime'] = df['dropoff_datetime'].astype(str)

    # Step 5: Insert in batches
    conn = get_connection()
    batch_size = 10000
    total = len(df)
    inserted = 0

    print(f"Inserting {total} records into database...")

    for i in range(0, total, batch_size):
        batch = df.iloc[i:i+batch_size]
        batch.to_sql('trips', conn, if_exists='append', index=False)
        inserted += len(batch)
        print(f"Progress: {inserted}/{total} records inserted", end='\r')

    conn.close()
    print(f"\nDone! {inserted} records loaded into {DB_PATH}")

if __name__ == "__main__":
    load_data()