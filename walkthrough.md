# Precision Farming System: Setup and Testing Walkthrough

This document outlines the steps taken to run and verify the end-to-end functionality of the Precision Farming System.

## 1. Project Setup
The project was run using Docker Compose, which automates the orchestration of the following services:
- **Mosquitto**: MQTT Broker for telemetry data.
- **InfluxDB**: Time-series database for sensor readings.
- **PostgreSQL**: Relational database for farm metadata and ML recommendations.
- **Grafana**: Visualization dashboard.
- **Ingestor**: Python service that routes MQTT data to InfluxDB.
- **Backend**: FastAPI REST API for managing the system.
- **ML Worker**: Python service that generates irrigation and fertilizer recommendations.

### Key Improvements Made:
- **Docker Logging**: Updated `docker-compose.yml` to remove the obsolete `version` tag and added the `-u` flag to Python commands for real-time (unbuffered) logging.
- **Auto-Provisioned Dashboards**: Created a `Farm Overview` JSON dashboard and configured Grafana to load it automatically on startup.
- **API Robustness**: Updated the Backend to use case-insensitive SQL matching (`ILIKE`) for `zone_id` lookups.

---

## 2. Verification Steps

### 📈 Sensor Telemetry Ingestion
We simulated a sensor reading by publishing an MQTT message to the `mosquitto` broker. We verified that the `ingestor` service correctly received the message and saved it to InfluxDB.

**Test Command:**
```cmd
docker exec mosquitto mosquitto_pub -t "telemetry/1/Zone_A/sensor_01" -m "{\"battery\": 4.2, \"sensors\": {\"soil_moisture\": 22.0, \"temperature\": 31.0, \"humidity\": 40.0, \"nitrogen\": 60}}"
```

### 🧠 AI Recommendation Generation
By simulating a "Drought" (Soil Moisture = 22%), we triggered the `ml_worker` reasoning logic.

**Validation:**
Checked the `ml_worker` logs and confirmed it successfully generated:
- A **WATER** recommendation (Dry soil).
- A **FERTILIZER** recommendation (Low Nitrogen).

### 🌐 API Access
We verified that the Recommendations can be accessed via the Backend API:
- **URL:** [http://localhost:8000/api/v1/recommendations/Zone_A](http://localhost:8000/api/v1/recommendations/Zone_A)
- **Result:** Successfully returned a JSON array of pending actions.

### 📊 Grafana Visualization
The `Farm Overview` dashboard correctly visualizes the soil moisture, temperature, and humidity trends as new data points are received.

---

## 3. Conclusion
The system is now fully operational. You can continue testing by sending more simulated MQTT messages or by integrating physical ESP32 devices to the `mosquitto` broker on port `1883`.
