# subscribes to a topic and recieves messages from the publisher 

from kafka import KafkaConsumer

def main():
    print("Creating the subscriber...")

    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        group_id='debug-group-1',
        enable_auto_commit=True
    )

    print("Kafka consumer subscribed topics:", consumer.topics())
    print("Listening for messages...")

    for message in consumer:
        print(f"Received: {message.value.decode()}")

if __name__ == "__main__":
    main()


