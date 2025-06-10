# subscribes to a topic and recieves messages from the publisher 

from kafka import KafkaConsumer

message = ""

def main():
    print("Creating the subscriber...")

    consumer = KafkaConsumer(
        'room_1_HVAC', 'room_2_HVAC',
        bootstrap_servers='localhost:9093',
        auto_offset_reset='earliest',
        group_id='debug-group-1',
        enable_auto_commit=True
    )

    print("Kafka consumer subscribed topics:", consumer.topics())
    
    print("Listening for messages...")

    for command in consumer:
        global message

        print(f"Received from topic '{command.topic}': {command.value.decode()}")

        hvacCommand = command.value.decode()
        if(hvacCommand != message):
            if(hvacCommand == "off"):
                print (command.topic + ": Turning HVAC off")
            if(hvacCommand == "cooling"):
                print(command.topic + ": Turning HVAC on (cooling)")
            if(hvacCommand == "heating"):
                print(command.topic + ": Turning HVAC off (heating)")
        
        message = hvacCommand; 

if __name__ == "__main__":
    main()


