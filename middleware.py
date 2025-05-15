from kafka import KafkaProducer
from kafka import KafkaConsumer
import json

# dont need this if using dataset 
def generate_temperature_data(sensor_id: str) -> dict:
    """Generate random temperature data for a sensor."""
    import random
    return {
        'sensor_id': sensor_id,
        'temperature': random.randint(65, 80)
    }


def publish_temperature(producer, topic: str, data: dict):
    """Send temperature data to Kafka topic."""
    producer.send(topic, data)

def publish_user_feedback(producer, user_id: str, comfort_status: str):
    """Publish feedback to Kafka topic."""
    data = {'user': user_id, 'status': comfort_status}
    producer.send('user_feedback', data)

# for user feeback 
def evaluate_comfort(current_temp: float, preferred_temp: float) -> str:
    """Determine user's comfort status."""
    if current_temp > preferred_temp + 1:
        return "too hot"
    elif current_temp < preferred_temp - 1:
        return "too cold"
    else:
        return "comfortable"

def publish_hvac_command(producer, command: str):
    """Send control command to HVAC topic."""
    data = {'command': command}
    producer.send('hvac_commands', data)

def handle_hvac_command(command: str):
    """Simulate HVAC system behavior based on control command."""
    print(f"HVAC action: {command}")

def log_event(event_type: str, data: dict, filename='system_log.csv'):
    """Log events (sensor, feedback, command) to a CSV file."""
    import csv, os
    exists = os.path.exists(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['event_type', 'data'])
        if not exists:
            writer.writeheader()
        writer.writerow({'event_type': event_type, 'data': str(data)})

def aggregate_feedback(feedback_window: list) -> str:
    """Determine majority comfort level from recent feedback."""
    from collections import Counter
    count = Counter(feedback_window)
    if count['too hot'] >= 3:
        return 'increase AC'
    elif count['too cold'] >= 3:
        return 'decrease AC'
    else:
        return 'do nothing'



def connect_kafka_producer():
    """Initialize Kafka producer with JSON serializer."""
    
    import json
    return KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def connect_kafka_consumer(topic: str, group_id: str = None):
    """Initialize Kafka consumer for a topic."""
    return KafkaConsumer(
        topic,
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id=group_id
    )
