import pyodbc
import random
import time
from datetime import datetime
from config import BaseConfig as app

# ---------------------------------------------------------------------
# CONFIGURATION SECTION
# ---------------------------------------------------------------------

# Replace the server name with your actual SQL Server instance.
# This assumes Windows Authentication and encryption handling.
conn_str = (
    f'Driver={app.DRIVER}; \
    Server={app.SERVER_LOCAL}; \
    Database={app.DATABASE}; \
    UID={app.USN}; \
    PWD={app.PWD}; \
    TrustServerCertificate=yes;'
)

# --- STATIC IDs ---
# Set these to known valid values in your system
vehicle_id = 5  # <-- Set your VehicleID here
driver_id = 2  # <-- Set your DriverID here

# Dictionary of all sensor codes with industry standard ranges
sensor_codes = {
    "ENG_TEMP": (60, 115),  # Engine Temperature in Celsius
    "OIL_PRESS": (20, 80),  # Oil Pressure in psi
    "BAT_VOLT": (11.5, 14.8),  # Battery Voltage in Volts
    "FUEL_LVL": (0, 100),  # Fuel Level in percentage
    "TIRE_PRESS": (28, 36),  # Tire Pressure in psi
    "RPM": (700, 3000),  # Engine RPM
    "SPEED": (0, 130),  # Speed in km/h
    "ACCEL_X": (-3.0, 3.0),  # Acceleration on X axis in G
    "ODOMETER": (10000, 500000),  # Odometer in km
}

# ---------------------------------------------------------------------
# FUNCTION DEFINITIONS
# ---------------------------------------------------------------------


def get_next_sensor_value(sensor_code):
    """Returns a simulated sensor value within a configured range."""
    low, high = sensor_codes[sensor_code]
    return round(random.uniform(low, high), 2)


def get_sensor_id(cursor, sensor_code):
    """Retrieves the SensorID from DimTelemetrySensor given the SensorCode."""
    cursor.execute(
        "SELECT SensorID FROM DimTelemetrySensor WHERE SensorCode = ?", sensor_code
    )
    row = cursor.fetchone()
    return row[0] if row else None


# ---------------------------------------------------------------------
# MAIN STREAMING LOGIC
# ---------------------------------------------------------------------

conn = None
cursor = None

try:
    # Establish SQL Server connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected to SQL Server.")

    try:
        # Truncate table before run
        cursor.execute("TRUNCATE TABLE [dbo].[FactVehicleTelemetryStream];")
        conn.commit()
        print("Truncated table [dbo].[FactVehicleTelemetryStream].")
    except pyodbc.Error as e:
        print(f"[TRUNCATE ERROR] {e}")

    for i in range(100):  # Simulate 100 streaming intervals
        timestamp = datetime.utcnow()
        date_id = int(timestamp.strftime("%Y%m%d"))  # e.g., 20250523
        hour_min_label = timestamp.strftime("%H:%M")  # returns string like '14:35'
        print(f"\n[{timestamp}] Streaming set {i + 1}/100")
        print(f"\n Hour & Min [{hour_min_label}]\n")

        for sensor_code in sensor_codes:
            sensor_id = get_sensor_id(cursor, sensor_code)

            if sensor_id is None:
                print(
                    f"[WARNING] Sensor '{sensor_code}' not found in DimTelemetrySensor."
                )
                continue

            value = get_next_sensor_value(sensor_code)

            cursor.execute(
                """
                INSERT INTO dbo.FactVehicleTelemetryStream (
                    VehicleID, DriverID, SensorID, Value, StreamTimestamp, StreamHourMin, DateID
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                vehicle_id,
                driver_id,
                sensor_id,
                value,
                timestamp,
                hour_min_label,
                date_id,
            )

        conn.commit()
        print(
            f"[SUCCESS] Streamed all sensors for VehicleID={vehicle_id}, DriverID={driver_id}"
        )
        time.sleep(1)

except pyodbc.Error as db_err:
    print(f"[DATABASE ERROR] {db_err}")
except Exception as ex:
    print(f"[ERROR] {ex}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Database connection closed.")
