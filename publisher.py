# published messages to a topic 
import pandas as pd

from kafka import KafkaProducer

def publish_HVAC_command(command, topic): 
    print("Got HVAC command: ", command, "from ", topic)
    #producer.send(topic, command)
    #print('Sent:' + command.decode('utf-8'))


def main():
    room_file = "/Users/asad/SmartRoom/Room1.csv"
    df = pd.read_csv(room_file)
    print (linear_reg(df, 5, "/Users/asad/SmartRoom/room1_output_logs/testing.csv"))
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    topic = 'test-topic'
    publish_HVAC_command('Hello'.encode('utf-8'), producer, topic)
    producer.flush()
    producer.close()
if __name__ == "__main__":
    main()



