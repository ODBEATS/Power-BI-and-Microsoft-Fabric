import pyodbc
import random
import time
from datetime import datetime
from config import BaseConfig as app

# --- CONFIGURATION SECTION ---
# Set the starting city for the simulated GPS stream.
# Options: "San Francisco" or "San Diego"
CITY = "San Francisco"  # Change to "San Diego" if desired

# Dictionary mapping city names to their latitude and longitude coordinates.
city_coords = {
    "San Francisco": (37.7749, -122.4194),
    "San Diego": (32.7157, -117.1611)
}

# Unpack the starting latitude and longitude for the selected city.
start_lat, start_lon = city_coords[CITY]

# Simulated trip and driver metadata.
# These IDs should correspond to valid records in your database.
driver_id = 2
vehicle_id = 5
trip_id = 30

# SQL Server connection string.
# Replace the placeholders with your actual database credentials and settings.
conn_str = (
    f"Driver={app.DRIVER}; \
    Server={app.SERVER_LOCAL}; \
    Database={app.DATABASE}; \
    UID={app.USN}; \
    PWD={app.PWD}; \
    TrustServerCertificate=yes;"
)

# Predefine connection and cursor for safe cleanup in the finally block.
conn = None
cursor = None

def get_next_coords(lat, lon):
    """
    Simulate the next GPS coordinates by randomly moving the current point.
    Args:
        lat (float): Current latitude.
        lon (float): Current longitude.
    Returns:
        tuple: New latitude and longitude, rounded to 6 decimal places.
    """
    delta_lat = random.uniform(-0.0007, 0.0007)
    delta_lon = random.uniform(-0.0007, 0.0007)
    return round(lat + delta_lat, 6), round(lon + delta_lon, 6)

try:
    # Attempt to connect to the SQL Server database.
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # --- RETRIEVE A VALID TripID, VehicleID, DriverID FROM DATABASE ---
    # This ensures the stream uses valid references.
    cursor.execute("""
        SELECT TOP 1 TripID, VehicleID, DriverID
        FROM FactTripSummary
        ORDER BY NEWID()
    """)
    row = cursor.fetchone()
    if not row:
        # If no trip records are found, raise an exception to halt execution.
        raise Exception("No Trip records found in FactTripSummary.")
    # Optionally, use the retrieved IDs instead of hardcoded ones:
    # trip_id, vehicle_id, driver_id = row

    print(f"Streaming for TripID={trip_id}, VehicleID={vehicle_id}, DriverID={driver_id}")

    # --- STREAM SIMULATED GEOLOCATION DATA TO DATABASE ---
    lat, lon = start_lat, start_lon

    for _ in range(100):  # Stream 100 GPS points
        lat, lon = get_next_coords(lat, lon)
        timestamp = datetime.utcnow()  # Use UTC for consistency
        date_id = int(timestamp.strftime("%Y%m%d"))  # e.g., 20250523
        try:
            # Insert the simulated GPS data into the FactTripGeoStream table.
            cursor.execute("""
                INSERT INTO dbo.FactTripGeoStream (
                    TripID, VehicleID, DriverID, Latitude, Longitude, StreamTimestamp, DateID
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, trip_id, vehicle_id, driver_id, lat, lon, timestamp, date_id)

            conn.commit()
            print(f"Inserted: {lat}, {lon} at {timestamp}")
        except pyodbc.Error as db_err:
            # Handle database-specific errors for each insert.
            print(f"Database insert error at {timestamp}: {db_err}")
            # Optionally, break or continue depending on severity.
            continue

        time.sleep(1)  # Simulate a 1-second interval between GPS points

except pyodbc.Error as db_conn_err:
    # Handle errors related to database connection or setup.
    print(f"Database connection/setup error: {db_conn_err}")
except Exception as e:
    # Handle all other exceptions.
    print(f"ERROR: {e}")
finally:
    # Ensure resources are properly released.
    if cursor:
        try:
            cursor.close()
        except Exception as close_err:
            print(f"Error closing cursor: {close_err}")
    if conn:
        try:
            conn.close()
        except Exception as close_err:
            print(f"Error closing connection: {close_err}")
