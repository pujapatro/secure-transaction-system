from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import math
from datetime import datetime

app = FastAPI()

DB_NAME = "orders.db"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

conn = get_db()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT,
    latitude REAL,
    longitude REAL,
    weight INTEGER,
    priority TEXT,
    vehicle TEXT,
    distance_km REAL,
    delivery_cost REAL,
    created_at TEXT
)
""")
conn.commit()

# ---------- MODEL ----------
class Order(BaseModel):
    order_id: str
    latitude: float
    longitude: float
    weight: int
    priority: str

# ---------- LOGIC ----------
WAREHOUSE_LAT = 19.0760
WAREHOUSE_LON = 72.8777

def calculate_distance(lat, lon):
    return round(
        math.sqrt((lat - WAREHOUSE_LAT) ** 2 + (lon - WAREHOUSE_LON) ** 2) * 111,
        2
    )

def assign_vehicle(weight, order_id):
    ev_toggle = int(order_id.split("_")[1]) % 2 == 0

    if weight <= 100:
        if ev_toggle:
            return "3W EV", 4
        return "3W", 6
    else:
        if ev_toggle:
            return "4W EV", 7
        return "4W", 10

# ---------- API ----------
@app.post("/orders")
def create_order(order: Order):
    distance = calculate_distance(order.latitude, order.longitude)
    vehicle, cost_per_km = assign_vehicle(order.weight, order.order_id)
    cost = round(distance * cost_per_km, 2)

    cursor.execute("""
        INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order.order_id,
        order.latitude,
        order.longitude,
        order.weight,
        order.priority,
        vehicle,
        distance,
        cost,
        datetime.utcnow().isoformat()
    ))
    conn.commit()

    return {"status": "success"}

@app.get("/orders")
def get_orders():
    cursor.execute("SELECT * FROM orders")
    return cursor.fetchall()
