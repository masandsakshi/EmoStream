# app_new.py
from flask import Flask, request, jsonify, render_template
from kafka import KafkaProducer
from flask_socketio import SocketIO
import json
import threading
from kafka import KafkaConsumer

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    linger_ms=500
)

clients = {}

@app.route('/register', methods=['POST'])
def register_client():
    data = request.get_json()
    client_id = data['client_id']
    subscriber = data['subscriber']
    clients[client_id] = subscriber
    return jsonify({'status': 'registered'}), 200

@app.route('/deregister', methods=['POST'])
def deregister_client():
    data = request.get_json()
    client_id = data['client_id']
    if client_id in clients:
        del clients[client_id]
        return jsonify({'status': 'deregistered'}), 200
    return jsonify({'status': 'not found'}), 404

@app.route('/emoji', methods=['POST'])
def receive_emoji():
    data = request.get_json()
    producer.send('emoji_topic', value=data)
    return jsonify({'status': 'success'}), 200

@app.route('/')
def index():
    return render_template('index.html')

def consume_aggregated_data():
    consumer = KafkaConsumer(
        'emoji_topic_aggregated',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id='websocket_group'
    )
    for message in consumer:
        data = message.value
        if 'emoji_type' in data and 'final_count' in data:
            emit_data = {
                'emoji_type': data['emoji_type'],
                'final_count': int(data['final_count'])
            }
            socketio.emit('emoji_data', emit_data)

thread = threading.Thread(target=consume_aggregated_data)
thread.daemon = True
thread.start()

if __name__ == '__main__':
    socketio.run(app, port=5000)