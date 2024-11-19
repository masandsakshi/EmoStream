# client_sender.py
import requests
import random
import time
import uuid
from datetime import datetime

emojis = ['😀', '😂', '🥰', '😢', '😡']

def register_client():
    user_id = str(uuid.uuid4())
    response = requests.post('http://localhost:5000/register', json={"client_id": user_id, "subscriber": "subscriber_topic"})
    if response.status_code == 200:
        print(f"Registered client: {user_id}")
        return user_id
    else:
        print("Failed to register client")
        return None

def send_emoji(user_id):
    while True:
        data = {
            "user_id": user_id,
            "emoji_type": random.choice(emojis),
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post('http://localhost:5000/emoji', json=data)
        if response.status_code == 200:
            print(f"Sent emoji: {data}")
        time.sleep(0.01)  # Send 100 emojis per second

if __name__ == "__main__":
    user_id = register_client()
    if user_id:
        send_emoji(user_id)