# # server.py
# from fastapi import FastAPI, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# import asyncio
# from typing import List
# from threading import Thread
# import json
# from kafka import KafkaConsumer

# app = FastAPI()
# clients: List[WebSocket] = []
# main_loop = asyncio.get_event_loop()


# # In-memory buffer
# shared_buffer = []
# buffer_lock = asyncio.Lock()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket client connected")
#     clients.append(websocket)
#     try:
#         while True:
#             await asyncio.sleep(0.1)
#     except Exception as e:
#         print("WebSocket error:", e)
#     # finally:
#     #     clients.remove(websocket)

# def kafka_listener():
#     consumer = KafkaConsumer(
#         'room_1_UI', 'room_2_UI',
#         bootstrap_servers='localhost:9092',
#         value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#         auto_offset_reset='latest',
#         group_id='dashboard-group',
#     )

#     for msg in consumer:
#         print("IN SERVER: Kafka message received:", msg.value)
#         asyncio.run_coroutine_threadsafe(forward_to_clients(msg.topic, msg.value), main_loop)

# async def forward_to_clients(topic, data):
#     structured_data = {
#         "roomID": topic,
#         "time": data["time"],
#         "room_temp": data["room_temp"],
#         "energy": data["energy"],
#         "command": data["command"]
#     }

#     print("IN SERVER Sending Live to Clients: ", structured_data)

#     for ws in clients:
#         try:
#             await ws.send_json(structured_data)
#         except Exception as e:
#             print("WebSocket send failed:", e)

# @app.on_event("startup")
# async def startup_event():
#     Thread(target=kafka_listener, daemon=True).start()


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

# In-memory buffer and lock for thread-safety
shared_buffer = []
buffer_lock = asyncio.Lock()
MAX_BUFFER_SIZE = 100  # adjust as needed

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected")
    # Send all buffered messages immediately upon connection.
    async with buffer_lock:
        for msg in shared_buffer:
            try:
                await websocket.send_json(msg)
            except Exception as e:
                print("Failed to send buffered message:", e)
    clients.append(websocket)
    try:
        while True:
            # This loop keeps the connection open.
            await asyncio.sleep(0.1)
    except Exception as e:
        print("WebSocket error:", e)
    finally:
        if websocket in clients:
            clients.remove(websocket)
        print("WebSocket client disconnected")

def kafka_listener():
    consumer = KafkaConsumer(
        'room_1_UI', 'room_2_UI',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        group_id='dashboard-group',
    )
    for msg in consumer:
        print("IN SERVER: Kafka message received:", msg.value)
        asyncio.run_coroutine_threadsafe(forward_to_clients(msg.topic, msg.value), main_loop)

async def forward_to_clients(topic, data):
    structured_data = {
        "roomID": topic,
        "time": data["time"],
        "room_temp": data["room_temp"],
        "energy": data["energy"],
        "command": data["command"]
    }
    
    # Buffer the new message.
    async with buffer_lock:
        shared_buffer.append(structured_data)
        # Remove oldest messages if buffer exceeds capacity.
        if len(shared_buffer) > MAX_BUFFER_SIZE:
            shared_buffer.pop(0)
    
    print("IN SERVER Sending Live to Clients: ", structured_data)
    
    dead_clients = []
    for ws in clients:
        try:
            await ws.send_json(structured_data)
        except Exception as e:
            print("WebSocket send failed:", e)
            dead_clients.append(ws)
    
    # Remove any connections that failed.
    for ws in dead_clients:
        if ws in clients:
            clients.remove(ws)

@app.on_event("startup")
async def startup_event():
    Thread(target=kafka_listener, daemon=True).start()
