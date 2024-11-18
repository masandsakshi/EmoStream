# client_sender.py
import requests
import random
import time
import uuid

from datetime import datetime

emojis = ['😀', '😂', '🥰', '😢', '😡']

def send_emoji():
    user_id = str(uuid.uuid4())
    while True:
        data = {
            "user_id": user_id,
            "emoji_type": random.choice(emojis),
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post('http://localhost:5000/emoji', json=data)
        time.sleep(0.005)

if __name__ == "__main__":
    send_emoji()
