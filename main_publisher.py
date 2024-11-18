# main_publisher.py
from kafka import KafkaConsumer, KafkaProducer
import json

consumer = KafkaConsumer(
    'emoji_topic_aggregated',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for message in consumer:
    data = message.value
    # Forward the aggregated data to cluster_topic
    producer.send('cluster_topic', value=data)