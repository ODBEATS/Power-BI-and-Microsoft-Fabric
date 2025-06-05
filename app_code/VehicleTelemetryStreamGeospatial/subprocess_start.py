import subprocess

# Use subprocess to launch scripts from a controller script
subprocess.Popen(["python", "app_code/VehicleTelemetryStreamGeospatial/VehicleTelemetryStream.py"])
subprocess.Popen(["python", "app_code/VehicleTelemetryStreamGeospatial/VehicleTelemetryStreamGeospatial.py"])
#subprocess.Popen(["python", "VehicleTelemetryStreamGeospatial_osmnx.py"])


