import paho.mqtt.client as mqtt
import time
import json
import random

BROKER = "localhost"
PORT = 1883
FARM_ID = "1"
ZONE_ID = "Zone_A"
DEVICE_ID = "00:1B:44:11:3A:B7"
TOPIC = f"telemetry/{FARM_ID}/{ZONE_ID}/{DEVICE_ID}"

client = mqtt.Client(f"simulator_{DEVICE_ID}")
client.connect(BROKER, PORT, 60)

print(f"Starting IoT Simulator for Farm {FARM_ID}, Zone {ZONE_ID}...")

try:
    while True:
        payload = {
            "timestamp": int(time.time()),
            "battery": round(random.uniform(3.5, 4.2), 2),
            "sensors": {
                "soil_moisture": round(random.uniform(20.0, 40.0), 1),
                "temperature": round(random.uniform(18.0, 35.0), 1),
                "humidity": round(random.uniform(40.0, 80.0), 1),
                "nitrogen": int(random.uniform(30, 70)),
                "phosphorus": int(random.uniform(20, 80)),
                "potassium": int(random.uniform(100, 250))
            }
        }
        client.publish(TOPIC, json.dumps(payload), qos=1)
        print(f"Published: {payload}")
        time.sleep(10) # Publish every 10 seconds for testing
except KeyboardInterrupt:
    print("Simulator stopped.")
    client.disconnect()
