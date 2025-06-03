# subscribes to a topic and recieves messages from the publisher 

from kafka import KafkaConsumer

message = ""

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
        global message

        hvacCommand = command.value.decode()
        if(hvacCommand != message):
            if(hvacCommand == "off"):
                print ("Turning HVAC off")
            if(hvacCommand == "cooling"):
                print("turning HVAC on (cooling)")
            if(hvacCommand == "heating"):
                print("turning HVAC off (heating)")
        
        message = hvacCommand; 
        
        print(f"Received from topic '{command.topic}': {command.value.decode()}")

if __name__ == "__main__":
    main()


