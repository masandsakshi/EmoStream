# subscriber.py
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'subscriber_topic_2',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    data = message.value
    print(f"Received aggregated data: {data}")