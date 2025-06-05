# # subscribes to a topic and recieves messages from the publisher 

# from kafka import KafkaConsumer
# import json

# def main():
#     print("Creating the subscriber...")

#     consumer = KafkaConsumer(
#         'room_1', 'room_2',
#         bootstrap_servers='localhost:9092',
#         auto_offset_reset='earliest',
#         group_id='debug-group-1',
#         enable_auto_commit=True
#     )

#     print("Kafka consumer subscribed topics:", consumer.topics())
#     print("Listening for messages...")

#     for command in consumer:
#         decoded = json.loads(command.value.decode())
#         print(f"Decoded list: {decoded}")
# if __name__ == "__main__":
#     main()

from kafka import KafkaConsumer
import json

def main():
    print("Creating the subscriber...")

    consumer = KafkaConsumer(
        'room_1', 'room_2',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        group_id='debug-group-1',
        enable_auto_commit=True
    )

    print("Kafka consumer subscribed topics:", consumer.topics())
    print("Listening for messages...")

    for command in consumer:
        try:
            decoded = json.loads(command.value.decode())
            print(f"Decoded list: {decoded}")
        except json.JSONDecodeError:
            print(f"Invalid JSON message skipped: {command.value}")
        except Exception as e:
            print(f"Error decoding message: {e}")

if __name__ == "__main__":
    main()

