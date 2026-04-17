import os
import sqlite3
import pandas as pd
import requests

# ─── CONFIG ─────────────────────────────────────────────
DROPBOX_URL = "https://www.dropbox.com/scl/fi/089cqooyrgf472dmob3x0/train.csv?rlkey=zhwuoizy4s9bach2ujiqmw4tf&st=7kpsaioy&dl=1"

CSV_FILE = "train.csv"
DB_FILE = "taxi.db"


# ─── STEP 1: Download CSV from Dropbox ──────────────────
def download_file(url, output):
    print("Downloading dataset from Dropbox...")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(output, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print("Download complete!")


if not os.path.exists(CSV_FILE):
    download_file(DROPBOX_URL, CSV_FILE)
else:
    print("CSV already exists, skipping download.")


# ─── STEP 2: Load data ──────────────────────────────────
print("Loading data...")

if not os.path.exists(CSV_FILE):
    raise Exception("CSV file not found after download.")

df = pd.read_csv(CSV_FILE)

print("Data loaded!")
print("Columns found:", list(df.columns))


# ─── STEP 3: Data processing ────────────────────────────
print("Processing data...")

required_cols = ["pickup_datetime", "dropoff_datetime"]

for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Missing required column: {col}")

df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"])

df["duration_minutes"] = (
    (df["dropoff_datetime"] - df["pickup_datetime"]).dt.total_seconds() / 60
)

df["pickup_hour"] = df["pickup_datetime"].dt.hour
df["day_of_week"] = df["pickup_datetime"].dt.dayofweek

df = df[df["duration_minutes"] > 0]

if "trip_distance" in df.columns:
    df["speed_kmh"] = df["trip_distance"] / (df["duration_minutes"] / 60)
else:
    print("trip_distance not found → setting speed_kmh = 0")
    df["speed_kmh"] = 0


# ─── STEP 4: Save to SQLite ─────────────────────────────
print("Creating database...")

conn = sqlite3.connect(DB_FILE)
df.to_sql("trips", conn, if_exists="replace", index=False)
conn.close()

print("SUCCESS!")
print(f"Database created: {DB_FILE}")
print("You can now run: cd ../api then python app.py")