import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'taxi.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS trips (
            id                  TEXT PRIMARY KEY,
            vendor_id           INTEGER,
            pickup_datetime     TEXT,
            dropoff_datetime    TEXT,
            passenger_count     INTEGER,
            pickup_longitude    REAL,
            pickup_latitude     REAL,
            dropoff_longitude   REAL,
            dropoff_latitude    REAL,
            store_and_fwd_flag  TEXT,
            trip_duration       INTEGER,
            trip_distance_km    REAL,
            speed_kmh           REAL,
            pickup_hour         INTEGER,
            day_of_week         INTEGER,
            duration_minutes    REAL
        );

        CREATE INDEX IF NOT EXISTS idx_pickup_hour ON trips(pickup_hour);
        CREATE INDEX IF NOT EXISTS idx_day_of_week ON trips(day_of_week);
        CREATE INDEX IF NOT EXISTS idx_duration ON trips(trip_duration);
        CREATE INDEX IF NOT EXISTS idx_passenger ON trips(passenger_count);
        CREATE INDEX IF NOT EXISTS idx_vendor ON trips(vendor_id);
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()