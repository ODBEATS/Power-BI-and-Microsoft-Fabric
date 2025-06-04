# Vehicle Telemetry Database Setup

This project uses a SQL Server database to store and analyze vehicle telemetry and geospatial data. The database backup file, `VehicleTelemetryDM.bak`, contains all necessary tables, schema, and sample data.

## Database Overview

The database is designed to support telemetry data ingestion and geospatial analysis. Typical tables may include:

- **Vehicles**: Stores vehicle metadata (e.g., VIN, make, model).
- **TelemetryData**: Contains time-series data such as speed, location, and sensor readings.
- **GeospatialData**: Holds processed geospatial information for mapping and analysis.

> **Note:** For detailed schema, refer to the database diagrams or use SQL Server Management Studio (SSMS) to explore the restored database.

## Prerequisites

- **SQL Server** (2016 or later recommended)
- **SQL Server Management Studio (SSMS)**
- Sufficient permissions to restore databases

## Restoring `VehicleTelemetryDM.bak` to Local SQL Server

1. **Copy the Backup File**
   - Place `VehicleTelemetryDM.bak` in a directory accessible by your SQL Server instance (e.g., `C:\Backups\`).

2. **Open SQL Server Management Studio (SSMS)**
   - Connect to your local SQL Server instance.

3. **Restore the Database**
   - Right-click on `Databases` in Object Explorer.
   - Select `Restore Database...`.
   - Choose `Device` and browse to select `VehicleTelemetryDM.bak`.
   - Set the destination database name (e.g., `VehicleTelemetryDM`).
   - Review the restore options and paths.
   - Click `OK` to start the restore process.

4. **Verify the Restore**
   - Refresh the `Databases` node.
   - Expand `VehicleTelemetryDM` to view tables and data.

## Troubleshooting

- Ensure your SQL Server service account has read access to the backup file location.
- If you encounter file path errors, use the `Relocate all files to folder` option during restore.

## Dependencies

- This project assumes a running SQL Server instance and access to SSMS.
- Python scripts in this repository may require additional Python packages (see `requirements.txt` if available).

---

For further questions or issues, please consult the SQL Server documentation or reach out to the project moderator.

