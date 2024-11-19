# emoji_stream_server.py
from flask import Flask, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
from kafka import KafkaConsumer
import json
import threading
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

class EmojiStreamer:
    def __init__(self):
        self.topics = [
            'subscriber_topic_1',
            'subscriber_topic_2',
            'subscriber_topic_3'
        ]
        
    def start_streaming(self):
        for topic in self.topics:
            thread = threading.Thread(target=self.consume_topic, args=(topic,))
            thread.daemon = True
            thread.start()
            
    def consume_topic(self, topic):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id=f'livestream_{topic}',
            auto_offset_reset='latest'
        )
        
        for message in consumer:
            data = message.value
            if data.get('final_count') == 1:
                socketio.emit('emoji_event', {
                    'topic': topic,
                    'emoji_type': data['emoji_type'],
                    'timestamp': time.time()
                })
                time.sleep(0.1)  # Rate limiting

@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    streamer = EmojiStreamer()
    streamer.start_streaming()
    socketio.run(app, port=5001)