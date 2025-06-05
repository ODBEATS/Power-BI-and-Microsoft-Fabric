##############################################################
#
# Optional approach to generate a realistic driving route
#
##############################################################
import sys
import pyodbc
import time
from datetime import datetime, timedelta
import random
import math
import openrouteservice
from app_code.config import BaseConfig as app

# --- CONFIGURATION SECTION ---
CITY = "San Francisco"  # Options: "San Francisco" or "San Diego"

# Known-good coordinates (start and end on main roads)
city_routes = {
    "San Francisco": {
        "start": (-122.4194, 37.7749),   # Market St near Civic Center
        "end": (-122.3929, 37.7913)      # Embarcadero / Financial District
    },
    "San Diego": {
        "start": (-117.1611, 32.7157),   # Downtown SD
        "end": (-117.1456, 32.7312)      # North Park
    }
}


# OpenRouteService API key (get yours at openrouteservice.org)
ORS_API_KEY = app.ORS_API_KEY  # Replace this with your actual API key

# SQL Server connection string
conn_str = (
    f"Driver={app.DRIVER}; \
    Server={app.SERVER_LOCAL}; \
    Database={app.DATABASE}; \
    UID={app.USN}; \
    PWD={app.PWD}; \
    TrustServerCertificate=yes;"
)

# Trip metadata
driver_id = 2
vehicle_id = 5
trip_id = 30
NUM_POINTS = 100

# --- ROUTE GENERATION FUNCTION ---

def generate_route_with_ors(city_name, num_points=100):
    """
    Generate a realistic driving route using fixed start and end points for known cities.
    """
    try:
        client = openrouteservice.Client(key=ORS_API_KEY)

        if city_name not in city_routes:
            raise ValueError(f"City '{city_name}' is not configured.")

        start = city_routes[city_name]["start"]
        end = city_routes[city_name]["end"]

        print(f"Requesting route from ORS: {start} → {end}")
        route = client.directions(
            coordinates=[start, end],
            profile='driving-car',
            format='geojson'
        )

        coords = route['features'][0]['geometry']['coordinates']  # (lon, lat)

        # Resample to num_points
        if len(coords) > num_points:
            step = len(coords) / num_points
            sampled = [coords[int(i * step)] for i in range(num_points)]
        elif len(coords) < num_points:
            sampled = coords + [coords[-1]] * (num_points - len(coords))
        else:
            sampled = coords

        # Convert to (lat, lon)
        gps_coords = [(lat, lon) for lon, lat in sampled]
        print(f"Generated route with {len(gps_coords)} points.")
        return gps_coords

    except Exception as e:
        print(f"[ROUTE ERROR] {e}")
        sys.exit(1)

# --- DATABASE STREAMING ---

conn = None
cursor = None

try:
    gps_coords = generate_route_with_ors(CITY, NUM_POINTS)

    print("Connecting to SQL Server...")
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:
        # Truncate table before run
        cursor.execute("TRUNCATE TABLE [dbo].[FactTripGeoStream];")
        conn.commit()
        print("Truncated table [dbo].[FactTripGeoStream].")
    except pyodbc.Error as e:
        print(f"[TRUNCATE ERROR] {e}")

    # Optionally override with random trip/vehicle/driver IDs from database
    cursor.execute("""
        SELECT TOP 1 TripID, VehicleID, DriverID
        FROM FactTripSummary
        ORDER BY NEWID()
    """)
    row = cursor.fetchone()
    if not row:
        raise Exception("No trip records found in FactTripSummary.")
    # Uncomment to use random values from DB:
    # trip_id, vehicle_id, driver_id = row

    print(f"Streaming GPS for TripID={trip_id}, VehicleID={vehicle_id}, DriverID={driver_id}")

    for i, (lat, lon) in enumerate(gps_coords):
        timestamp = datetime.utcnow() + timedelta(seconds=i)
        date_id = int(timestamp.strftime("%Y%m%d"))

        try:
            cursor.execute("""
                INSERT INTO dbo.FactTripGeoStream (
                    TripID, VehicleID, DriverID, Latitude, Longitude, StreamTimestamp, DateID
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, trip_id, vehicle_id, driver_id, lat, lon, timestamp, date_id)

            conn.commit()
            print(f"Inserted: {lat:.6f}, {lon:.6f} at {timestamp}")
        except pyodbc.Error as db_err:
            print(f"[DB INSERT ERROR] {timestamp}: {db_err}")
            continue

        time.sleep(1)

except pyodbc.Error as db_conn_err:
    print(f"[DB CONNECTION ERROR] {db_conn_err}")
except Exception as e:
    print(f"[GENERAL ERROR] {e}")
finally:
    if cursor:
        try:
            cursor.close()
        except Exception as e:
            print(f"Error closing cursor: {e}")
    if conn:
        try:
            conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")