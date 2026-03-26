from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from influxdb_client import InfluxDBClient
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Precision Farming API", description="MVP Core API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_USER = os.getenv("PG_USER", "farm_admin")
PG_PASS = os.getenv("PG_PASS", "farm_password")
PG_DB = os.getenv("PG_DB", "farm_precision")

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "supersecrettoken123")
INFLUX_ORG = os.getenv("INFLUX_ORG", "farm_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "farm_telemetry")

# InfluxDB Client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

def get_db():
    conn = psycopg2.connect(host=PG_HOST, user=PG_USER, password=PG_PASS, dbname=PG_DB)
    try:
        yield conn
    finally:
        conn.close()

class DeviceCreate(BaseModel):
    farm_id: int
    zone_id: str
    mac_address: str

from datetime import datetime

class Recommendation(BaseModel):
    id: int
    zone_id: str
    action_type: str
    suggested_amount: float
    reasoning_metrics: Optional[dict]
    status: str
    created_at: datetime

@app.get("/api/v1/farms/{farm_id}")
def get_farm(farm_id: int, db = Depends(get_db)):
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM farms WHERE id = %s", (farm_id,))
        farm = cur.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")
        return dict(farm)

@app.get("/api/v1/farms/{farm_id}/devices")
def get_devices(farm_id: int, db = Depends(get_db)):
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM devices WHERE farm_id = %s", (farm_id,))
        return [dict(row) for row in cur.fetchall()]

@app.post("/api/v1/devices")
def create_device(device: DeviceCreate, db = Depends(get_db)):
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(
                "INSERT INTO devices (farm_id, zone_id, mac_address) VALUES (%s, %s, %s) RETURNING id",
                (device.farm_id, device.zone_id, device.mac_address)
            )
            device_id = cur.fetchone()['id']
            db.commit()
            return {"id": device_id, "message": "Device created successfully"}
        except psycopg2.IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Device with MAC already exists or farm invalid")

@app.get("/api/v1/recommendations/{zone_id}", response_model=List[Recommendation])
def get_recommendations(zone_id: str, db = Depends(get_db)):
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM recommendations WHERE zone_id ILIKE %s AND status IN ('PENDING', 'COMPLETED') ORDER BY created_at DESC LIMIT 10", (zone_id,))
        return [dict(row) for row in cur.fetchall()]

@app.post("/api/v1/recommendations/{rec_id}/complete")
def complete_recommendation(rec_id: int, db = Depends(get_db)):
    cur = db.cursor()
    try:
        cur.execute("UPDATE recommendations SET status = 'COMPLETED' WHERE id = %s", (rec_id,))
        db.commit()
        return {"status": "success", "id": rec_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()

@app.get("/api/v1/sensors/{zone_id}")
def get_sensor_data(zone_id: str):
    query_api = influx_client.query_api()
    # Support both "Zone_A" and "zone_a" by using regex in Flux
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -24h)
      |> filter(fn: (r) => r.zone_id =~ /(?i)^{zone_id}$/)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 50)
    '''
    try:
        result = query_api.query(query, org=INFLUX_ORG)
        output = []
        for table in result:
            for record in table.records:
                output.append(record.values)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return FileResponse("backend/static/index.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Precision Farming API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
