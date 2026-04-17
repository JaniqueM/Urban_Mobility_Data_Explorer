"""
NYC Taxi Urban Mobility Explorer - Flask API
This serves analytics data from the cleaned SQLite database.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'taxi.db')

# ─── Custom Quick-Sort DSA Implementation ───────────────────────────────────
# Required: manually implemented algorithm (no sort_values, no built-in sort)
# Complexity: O(n log n) average, O(n²) worst case | Space: O(log n)

def quicksort(arr, key_fn=lambda x: x):
    """
    Custom quicksort implementation for ranking/sorting trip data.
    Uses in-place partitioning with median-of-three pivot selection.
    Time: O(n log n) avg  |  Space: O(log n) stack depth
    """
    def _partition(lst, lo, hi):
        # Median-of-three pivot
        mid = (lo + hi) // 2
        if key_fn(lst[lo]) > key_fn(lst[mid]):
            lst[lo], lst[mid] = lst[mid], lst[lo]
        if key_fn(lst[lo]) > key_fn(lst[hi]):
            lst[lo], lst[hi] = lst[hi], lst[lo]
        if key_fn(lst[mid]) > key_fn(lst[hi]):
            lst[mid], lst[hi] = lst[hi], lst[mid]
        pivot = key_fn(lst[mid])
        lst[mid], lst[hi - 1] = lst[hi - 1], lst[mid]
        i, j = lo, hi - 1
        while True:
            i += 1
            while key_fn(lst[i]) < pivot:
                i += 1
            j -= 1
            while key_fn(lst[j]) > pivot:
                j -= 1
            if i >= j:
                break
            lst[i], lst[j] = lst[j], lst[i]
        lst[i], lst[hi - 1] = lst[hi - 1], lst[i]
        return i

    def _quicksort(lst, lo, hi):
        if hi - lo < 10:  # Insertion sort for small arrays
            for k in range(lo + 1, hi + 1):
                item = lst[k]
                j = k - 1
                while j >= lo and key_fn(lst[j]) > key_fn(item):
                    lst[j + 1] = lst[j]
                    j -= 1
                lst[j + 1] = item
            return
        pivot_idx = _partition(lst, lo, hi)
        _quicksort(lst, lo, pivot_idx - 1)
        _quicksort(lst, pivot_idx + 1, hi)

    result = list(arr)
    if len(result) > 2:
        _quicksort(result, 0, len(result) - 1)
    elif len(result) == 2:
        if key_fn(result[0]) > key_fn(result[1]):
            result[0], result[1] = result[1], result[0]
    return result


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Top-level KPI summary."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*)                      AS total_trips,
            ROUND(AVG(duration_minutes),2) AS avg_duration_min,
            ROUND(AVG(speed_kmh),2)        AS avg_speed_kmh,
            ROUND(AVG(passenger_count),2)  AS avg_passengers,
            MIN(pickup_datetime)           AS earliest,
            MAX(pickup_datetime)           AS latest,
            SUM(CASE WHEN vendor_id=1 THEN 1 ELSE 0 END) AS vendor1_trips,
            SUM(CASE WHEN vendor_id=2 THEN 1 ELSE 0 END) AS vendor2_trips
        FROM trips
    """)
    row = dict(cur.fetchone())
    conn.close()
    return jsonify(row)


@app.route('/api/trips/by-hour', methods=['GET'])
def trips_by_hour():
    """Trip volume and average duration per hour of day."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            pickup_hour AS hour,
            COUNT(*)                       AS trip_count,
            ROUND(AVG(duration_minutes),2) AS avg_duration,
            ROUND(AVG(speed_kmh),2)        AS avg_speed
        FROM trips
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/trips/by-day', methods=['GET'])
def trips_by_day():
    """Trip volume per day of week (0=Mon, 6=Sun)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            day_of_week,
            COUNT(*)                       AS trip_count,
            ROUND(AVG(duration_minutes),2) AS avg_duration
        FROM trips
        GROUP BY day_of_week
        ORDER BY day_of_week
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/trips/by-duration', methods=['GET'])
def trips_by_duration():
    """Duration distribution (bucket 5-min intervals)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            CAST(duration_minutes / 5 AS INTEGER) * 5 AS bucket,
            COUNT(*) AS trip_count
        FROM trips
        WHERE duration_minutes <= 60
        GROUP BY bucket
        ORDER BY bucket
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/trips/by-passenger', methods=['GET'])
def trips_by_passenger():
    """Trip counts by passenger count."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT passenger_count, COUNT(*) AS trip_count,
               ROUND(AVG(duration_minutes),2) AS avg_duration
        FROM trips
        GROUP BY passenger_count
        ORDER BY passenger_count
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/trips/peak-hours-ranked', methods=['GET'])
def peak_hours_ranked():
    """
    Custom quicksort applied to rank hours by trip volume.
    Demonstrates the manually implemented DSA.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT pickup_hour AS hour, COUNT(*) AS trip_count,
               ROUND(AVG(duration_minutes),2) AS avg_duration
        FROM trips
        GROUP BY pickup_hour
    """)
    raw = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Use our custom quicksort (no sort_values / sorted() on the data)
    ranked = quicksort(raw, key_fn=lambda x: x['trip_count'])
    ranked.reverse()  # descending

    return jsonify({
        'algorithm': 'custom_quicksort',
        'complexity': {'time': 'O(n log n)', 'space': 'O(log n)'},
        'ranked': ranked
    })


@app.route('/api/trips/vendor-comparison', methods=['GET'])
def vendor_comparison():
    """Vendor 1 vs Vendor 2 comparison across dimensions."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            vendor_id,
            COUNT(*)                        AS total_trips,
            ROUND(AVG(duration_minutes),2)  AS avg_duration,
            ROUND(AVG(speed_kmh),2)         AS avg_speed,
            ROUND(AVG(passenger_count),2)   AS avg_passengers,
            ROUND(MIN(duration_minutes),2)  AS min_duration,
            ROUND(MAX(duration_minutes),2)  AS max_duration
        FROM trips
        GROUP BY vendor_id
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/trips/heatmap', methods=['GET'])
def heatmap_data():
    """Sample coordinates for pickup heatmap (max 8000 points)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT pickup_latitude AS lat, pickup_longitude AS lng
        FROM trips
        WHERE pickup_latitude BETWEEN 40.49 AND 40.92
          AND pickup_longitude BETWEEN -74.25 AND -73.70
        ORDER BY RANDOM()
        LIMIT 8000
    """)
    rows = [[r[0], r[1], 0.5] for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/trips/recent', methods=['GET'])
def recent_trips():
    """Paginated trip list with optional filters."""
    page      = int(request.args.get('page', 1))
    per_page  = int(request.args.get('per_page', 50))
    hour      = request.args.get('hour')
    dow       = request.args.get('dow')
    pax       = request.args.get('passengers')

    offset = (page - 1) * per_page
    where_clauses = []
    params = []

    if hour is not None:
        where_clauses.append('pickup_hour = ?')
        params.append(int(hour))
    if dow is not None:
        where_clauses.append('day_of_week = ?')
        params.append(int(dow))
    if pax is not None:
        where_clauses.append('passenger_count = ?')
        params.append(int(pax))

    where_sql = ('WHERE ' + ' AND '.join(where_clauses)) if where_clauses else ''

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(f'SELECT COUNT(*) FROM trips {where_sql}', params)
    total = cur.fetchone()[0]

    cur.execute(f"""
        SELECT id, vendor_id, pickup_datetime, dropoff_datetime,
               passenger_count, pickup_latitude, pickup_longitude,
               dropoff_latitude, dropoff_longitude,
               ROUND(duration_minutes,1) AS duration_min,
               ROUND(speed_kmh,1) AS speed_kmh,
               pickup_hour, day_of_week
        FROM trips {where_sql}
        ORDER BY pickup_datetime DESC
        LIMIT ? OFFSET ?
    """, params + [per_page, offset])

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    return jsonify({'total': total, 'page': page, 'per_page': per_page, 'trips': rows})


@app.route('/api/trips/monthly-trend', methods=['GET'])
def monthly_trend():
    """Trip volume broken down by month."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            SUBSTR(pickup_datetime, 1, 7) AS month,
            COUNT(*) AS trip_count,
            ROUND(AVG(duration_minutes),2) AS avg_duration,
            ROUND(AVG(speed_kmh),2) AS avg_speed
        FROM trips
        GROUP BY month
        ORDER BY month
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/trips/speed-distribution', methods=['GET'])
def speed_distribution():
    """Speed distribution bucketed by 5 km/h intervals."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            CAST(speed_kmh / 5 AS INTEGER) * 5 AS bucket,
            COUNT(*) AS count
        FROM trips
        WHERE speed_kmh BETWEEN 1 AND 100
        GROUP BY bucket
        ORDER BY bucket
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
