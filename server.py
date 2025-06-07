# server.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List
from threading import Thread
import json
from kafka import KafkaConsumer

app = FastAPI()
clients: List[WebSocket] = []
main_loop = asyncio.get_event_loop()


# In-memory buffer
shared_buffer = []
buffer_lock = asyncio.Lock()

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

# Kafka listener thread
def kafka_listener():
    consumer = KafkaConsumer(
        'room_1', 'room_2',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        group_id='dashboard-group'
    )
    for msg in consumer:
        print("Kafka message received:", msg.value)
        asyncio.run_coroutine_threadsafe(buffer_data(msg.value), main_loop)

# Add message to shared buffer
async def buffer_data(data):
    async with buffer_lock:
        shared_buffer.append(data)
        if len(shared_buffer) > 100:
            shared_buffer.pop(0)

# Push messages to connected WebSocket clients
async def pubsub_forwarder():
    while True:
        await asyncio.sleep(1)
        async with buffer_lock:
            if shared_buffer:
                latest = shared_buffer[-1]
                for ws in clients:
                    try:
                        await ws.send_json(latest)
                    except:
                        pass

@app.on_event("startup")
async def startup_event():
    Thread(target=kafka_listener, daemon=True).start()
    asyncio.create_task(pubsub_forwarder())
