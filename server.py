# server.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio

app = FastAPI()
clients: List[WebSocket] = []

# Allow frontend on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(0.1)
    except:
        clients.remove(websocket)

# Simulated Pub/Sub message processor
async def pubsub_listener():
    import random, datetime, json
    while True:
        data = {
            "room_id": "Room 1",
            "timestamp": str(datetime.datetime.now()),
            "actual_temp": round(random.uniform(21, 23), 2),
            "predicted_temp": round(random.uniform(21, 23), 2),
            "energy": round(random.uniform(0.1, 0.2), 2),
            "hvac_command": random.choice(["Cooling", "Heating", "Off"]),
        }
        for ws in clients:
            await ws.send_json(data)
        await asyncio.sleep(2)

@app.on_event("startup")
async def start_pubsub():
    asyncio.create_task(pubsub_listener())
