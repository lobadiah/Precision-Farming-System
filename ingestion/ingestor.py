import paho.mqtt.client as mqtt
import json
import os
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Config
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "supersecrettoken123")
INFLUX_ORG = os.getenv("INFLUX_ORG", "farm_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "farm_telemetry")

# Connect to InfluxDB with retry
influx_client = None
write_api = None

while True:
    try:
        influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        # Verify connection
        influx_client.ping()
        print("Connected to InfluxDB!")
        break
    except Exception as e:
        print(f"Waiting for InfluxDB... {e}")
        time.sleep(5)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe("telemetry/+/+/+")

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split('/')
        if len(topic_parts) != 4:
            return
            
        farm_id = topic_parts[1]
        zone_id = topic_parts[2]
        device_id = topic_parts[3]
        
        payload = json.loads(msg.payload.decode())
        sensors = payload.get("sensors", {})
        
        # Write to InfluxDB
        point = (
            Point("sensor_readings")
            .tag("farm_id", farm_id)
            .tag("zone_id", zone_id)
            .tag("device_id", device_id)
            .field("battery", payload.get("battery", 0.0))
            .field("soil_moisture", sensors.get("soil_moisture", 0.0))
            .field("temperature", sensors.get("temperature", 0.0))
            .field("humidity", sensors.get("humidity", 0.0))
            .field("nitrogen", sensors.get("nitrogen", 0))
            .field("phosphorus", sensors.get("phosphorus", 0))
            .field("potassium", sensors.get("potassium", 0))
        )
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"Ingested telemetry for Farm {farm_id}, Zone {zone_id} from {device_id}")
        
    except Exception as e:
        print(f"Ingestion error: {e}")

mqtt_client = mqtt.Client("ingestor_service")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

while True:
    try:
        print(f"Connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except Exception as e:
        print(f"Waiting for MQTT Broker... {e}")
        time.sleep(5)

print("Starting Ingestor Service Loop...")
mqtt_client.loop_forever()
