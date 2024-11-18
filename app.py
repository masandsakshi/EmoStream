# app.py
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    linger_ms=500  # Flush interval of 500 milliseconds
)

@app.route('/emoji', methods=['POST'])
def receive_emoji():
    data = request.get_json()
    producer.send('emoji_topic', value=data)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(port=5000)