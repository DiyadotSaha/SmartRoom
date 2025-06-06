from kafka import KafkaConsumer
import json
import threading
import time 

# Shared buffer for storing decoded messages
room_data_buffer = []
buffer_lock = threading.Lock()

def kafka_listener():
    global room_data_buffer

    consumer = KafkaConsumer(
        'room_1', 'room_2',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        group_id='debug-group-1',
        enable_auto_commit=True
    )

    print("Kafka consumer started.")
    for command in consumer:
        try:
            decoded = json.loads(command.value.decode())
            print(f"Decoded list: {decoded}")

            with buffer_lock:
                room_data_buffer.append(decoded)
                print(buffer_lock)
        except json.JSONDecodeError:
            print(f"Invalid JSON skipped: {command.value}")
        except Exception as e:
            print(f"Error decoding message: {e}")


def getRoomData():
    global room_data_buffer

    # Wait until buffer has at least one item
    while True:
        with buffer_lock:
            print("Buffer: " ,  room_data_buffer)
            if room_data_buffer:
                #data = room_data_buffer.pop(-1)  # pop the latest message
                #print("Returning and popping latest:", data)
                #return data

                return room_data_buffer
        
        # Sleep briefly to avoid busy-waiting
        time.sleep(0.1)

def main():
    # Start Kafka consumer in a background thread
    threading.Thread(target=kafka_listener, daemon=True).start()

    # Simulate UI polling
    import time
    while True:
        print("UI polling getRoomData():", getRoomData())
        time.sleep(5)

if __name__ == "__main__":
    main()
