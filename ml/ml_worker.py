import time
import os
import psycopg2
import json
from influxdb_client import InfluxDBClient

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "supersecrettoken123")
INFLUX_ORG = os.getenv("INFLUX_ORG", "farm_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "farm_telemetry")

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_USER = os.getenv("PG_USER", "farm_admin")
PG_PASS = os.getenv("PG_PASS", "farm_password")
PG_DB = os.getenv("PG_DB", "farm_precision")

influx_client = None
query_api = None

while True:
    try:
        influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        query_api = influx_client.query_api()
        influx_client.ping()
        print("Connected to InfluxDB!")
        break
    except Exception as e:
        print(f"Waiting for InfluxDB... {e}")
        time.sleep(5)

def get_pg_conn():
    while True:
        try:
            return psycopg2.connect(host=PG_HOST, user=PG_USER, password=PG_PASS, dbname=PG_DB)
        except Exception as e:
            print(f"Waiting for Postgres... {e}")
            time.sleep(5)

def generate_recommendations():
    print("Running ML recommendation engine...")
    conn = get_pg_conn()
    cur = conn.cursor()
    
    # 1. Fetch active devices/zones from Postgres
    cur.execute("SELECT DISTINCT zone_id FROM devices WHERE status='ACTIVE'")
    zones = [row[0] for row in cur.fetchall()]
    
    for zone in zones:
        # 2. Query last 1 hour of data from Influx for this zone
        query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r.zone_id == "{zone}")
          |> mean()
        '''
        try:
            tables = query_api.query(query, org=INFLUX_ORG)
            
            metrics = {}
            for table in tables:
                for record in table.records:
                    metrics[record.get_field()] = record.get_value()
                    
            if not metrics:
                print(f"No recent data for zone {zone}. Skipping.")
                continue
                
            print(f"Metrics for {zone}: {metrics}")
            
            sm = metrics.get('soil_moisture', 0)
            temp = metrics.get('temperature', 0)
            n = metrics.get('nitrogen', 0)
            
            # --- AUTOMATIC COMPLETION DETECTION ---
            # If the farmer took action (moisture rose or nitrogen rose), mark old PENDING tasks as COMPLETED
            # Using 60% for water and 90 for Nitrogen as "Good Enough" closure thresholds
            if sm > 60.0:
                cur.execute(
                    "UPDATE recommendations SET status='COMPLETED' WHERE zone_id=%s AND action_type='WATER' AND status='PENDING'",
                    (zone,)
                )
            if n > 90.0:
                cur.execute(
                    "UPDATE recommendations SET status='COMPLETED' WHERE zone_id=%s AND action_type='FERTILIZER' AND status='PENDING'",
                    (zone,)
                )
            
            recommendations_made = 0
            
            # Irrigation Logic heuristic implementation
            if sm < 45.0: # Match revised 80% target logic
                suggested_water = 80.0 - sm
                
                # Check for existing PENDING water recommendation
                cur.execute(
                    "SELECT id FROM recommendations WHERE zone_id=%s AND action_type='WATER' AND status='PENDING'",
                    (zone,)
                )
                if not cur.fetchone():
                    metrics_json = json.dumps({"current": sm, "target": 80.0})
                    cur.execute(
                        "INSERT INTO recommendations (zone_id, action_type, suggested_amount, reasoning_metrics) VALUES (%s, %s, %s, %s)",
                        (zone, 'WATER', round(suggested_water, 2), metrics_json)
                    )
                    recommendations_made += 1
                
            # Fertilizer Logic (Match 100 target logic)
            if n < 80:
                suggested_n = 100.0 - n
                
                # Check for existing PENDING fertilizer recommendation
                cur.execute(
                    "SELECT id FROM recommendations WHERE zone_id=%s AND action_type='FERTILIZER' AND status='PENDING'",
                    (zone,)
                )
                if not cur.fetchone():
                    metrics_json = json.dumps({"current": n, "target": 100.0})
                    cur.execute(
                        "INSERT INTO recommendations (zone_id, action_type, suggested_amount, reasoning_metrics) VALUES (%s, %s, %s, %s)",
                        (zone, 'FERTILIZER', round(suggested_n, 2), metrics_json)
                    )
                    recommendations_made += 1
                
            if recommendations_made > 0:
                conn.commit()
                print(f"Generated {recommendations_made} recommendations for {zone}")

        except Exception as e:
            conn.rollback()
            print(f"Error querying/writing for zone {zone}: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    print("Starting ML Worker Service...")
    while True:
        try:
            generate_recommendations()
        except Exception as e:
            print(f"ML Worker Error: {e}")
        time.sleep(60) # Run every minute for MVP testing
