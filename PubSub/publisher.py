# published messages to a topic 

from kafka import KafkaProducer

def main():
    print("creating the publisher")

    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    topic = 'test-topic'

    for i in range(5):
        msg = f'Hello {i}'.encode('utf-8')
        producer.send(topic, msg)
        print(f'Sent: Hello {i}')

    producer.flush()
    producer.close()

if __name__=="__main__":
    main()
