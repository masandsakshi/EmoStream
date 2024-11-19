# cluster_publisher.py
from kafka import KafkaConsumer, KafkaProducer
import json

consumer = KafkaConsumer(
    'cluster_topic_2',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for message in consumer:
    data = message.value
    # Forward data to multiple subscribers
    producer.send('subscriber_topic_1', value=data)
    producer.send('subscriber_topic_2', value=data)
    producer.send('subscriber_topic_3', value=data)