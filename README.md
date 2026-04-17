# NYC Taxi Urban Mobility Dashboard

## Project Overview

This project is a fullstack data application built using the New York City Taxi Trip dataset. It focuses on transforming raw trip-level data into meaningful insights about urban mobility patterns.

The system processes raw CSV data, stores it in a relational database, exposes it through a backend API, and visualizes trends through an interactive frontend dashboard.

---

## Objectives

* Clean and preprocess real-world taxi trip data
* Design a normalized relational database
* Build a backend service for efficient querying
* Develop a frontend dashboard for data exploration
* Extract and present meaningful insights

---

## System Architecture

```
Raw Dataset (CSV)
        ↓
Data Cleaning & Processing (Backend Script)
        ↓
Relational Database (SQLite/PostgreSQL)
        ↓
Backend API (Flask / Node.js)
        ↓
Frontend Dashboard (HTML, CSS, JavaScript)
```

---

## Tech Stack

### Backend

* Python (Data Processing)
* Flask (API) / Node.js (if used)

### Database

* SQLite / PostgreSQL

### Frontend

* HTML, CSS, JavaScript
* Chart.js (or other visualization library if used)

---

## Project Structure

```
project-root/
│
├── database/
│   ├── setup_db.py
│   └── clean.py
│   └── db_init.py
│   └── load.py
│
├── api/
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── index.css
│   └── index.js
│
├── README.md
```

---

## Data Processing

The raw dataset was cleaned and processed through the following steps:

* Removed missing and invalid records
* Converted timestamps into standard datetime format
* Filtered out unrealistic trip durations
* Handled outliers in distance and fare

### Derived Features

The following features were created:

* **Trip Duration (minutes)**
* **Trip Speed (km/h)**
* **Pickup Hour**
* **Day of Week**
* **Fare per Distance Ratio**

Suspicious or invalid records were excluded and logged during preprocessing.

---

## Database Design

The dataset was stored in a relational database with a structured schema.

### Example Table: `trips`

| Column           | Description       |
| ---------------- | ----------------- |
| id               | Unique trip ID    |
| pickup_datetime  | Trip start time   |
| dropoff_datetime | Trip end time     |
| duration_minutes | Trip duration     |
| trip_distance    | Distance traveled |
| fare_amount      | Total fare        |
| speed_kmh        | Derived speed     |

Indexes were applied to frequently queried fields such as:

* pickup_datetime
* trip_distance

---

## Backend API

The backend exposes endpoints to query taxi data.

### Example Endpoints

* `/trips` → Retrieve all trips
* `/trips?hour=...` → Filter by time
* `/stats` → Aggregated insights

The API enables dynamic data retrieval for the frontend dashboard.

---

## Frontend Dashboard

The frontend provides an interactive interface to explore the dataset.

### Features

* Filter trips by time, distance, or fare
* View summary statistics
* Visualize trends using charts
* Explore urban mobility patterns

### Example Visualizations

* Trips by hour of the day
* Average speed over time
* Fare vs distance distribution

---

## Insights (Examples)

* Peak taxi usage occurs during specific hours
* Trip speeds vary significantly based on time of day
* Certain trips show unusually high fare-to-distance ratios

---

## How to Run the Project

### 1. Clone the Repository

```
git clone https://github.com/JaniqueM/Urban_Mobility_data_Explorer.git
cd Urban_Mobility_data_Explorer
```

---

### 2. Install Dependencies

```
pip install -r api/requirements.txt
```

---

### 3. Run Data Processing

```
python database/setup_db.py
```

---

### 4. Start Backend Server

```
python api/app.py
```

---

### 5. Open Frontend

Open `frontend/index.html` in your browser
OR use a live server extension.

---

## Documentation

https://docs.google.com/document/d/1jkH0gpTQo_adKTFNiSs8cqbGPDU3HsRQ-CZCgNbOd_U/edit?usp=sharing

---

## Team Contributions

https://docs.google.com/spreadsheets/d/162lWpRD_iJIUlBUQVFr3_1dMTBCuD6M0CDDRpRD2E7E/edit?usp=sharing

---

## Future Improvements

* Add real-time data integration
* Improve performance with indexing and caching
* Enhance visualizations with maps and geospatial data
* Deploy fullstack application to cloud

---

## Contact

For questions or clarifications, contact the project team.
