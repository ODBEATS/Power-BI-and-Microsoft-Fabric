import subprocess

# Use subprocess to launch scripts from a controller script
subprocess.Popen(["python", "VehicleTelemetryStreamGeospatial/VehicleTelemetryStream.py"])
subprocess.Popen(["python", "VehicleTelemetryStreamGeospatial/VehicleTelemetryStreamGeospatial.py"])
#subprocess.Popen(["python", "VehicleTelemetryStreamGeospatial_osmnx.py"])


