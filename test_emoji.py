# test_emoji_system.py
import unittest
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from locust import HttpUser, task, between
import pytest
from datetime import datetime
import uuid

class TestEmojiAPI(unittest.TestCase):
    BASE_URL = "http://localhost:5000"
    
    def test_emoji_endpoint(self):
        """Test basic emoji endpoint functionality"""
        data = {
            "user_id": str(uuid.uuid4()),
            "emoji_type": "😀",
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(f"{self.BASE_URL}/emoji", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

    def test_client_registration(self):
        """Test client registration"""
        client_id = str(uuid.uuid4())
        data = {
            "client_id": client_id,
            "subscriber": "subscriber_topic_1"
        }
        response = requests.post(f"{self.BASE_URL}/register", json=data)
        self.assertEqual(response.status_code, 200)

    def test_concurrent_emoji_sending(self):
        """Test sending 100 emojis per second"""
        def send_emojis():
            user_id = str(uuid.uuid4())
            start_time = time.time()
            count = 0
            while count < 100:
                data = {
                    "user_id": user_id,
                    "emoji_type": "😀",
                    "timestamp": datetime.now().isoformat()
                }
                requests.post(f"{self.BASE_URL}/emoji", json=data)
                count += 1
            return time.time() - start_time

        elapsed = send_emojis()
        self.assertLess(elapsed, 1.1)  # Should take ~1 second

class LoadTest(HttpUser):
    wait_time = between(0.01, 0.1)
    
    def on_start(self):
        self.client_id = str(uuid.uuid4())
        self.register_client()
    
    def register_client(self):
        self.client.post("/register", json={
            "client_id": self.client_id,
            "subscriber": "subscriber_topic_1"
        })
    
    @task
    def send_emoji(self):
        self.client.post("/emoji", json={
            "user_id": self.client_id,
            "emoji_type": "😀",
            "timestamp": datetime.now().isoformat()
        })

@pytest.fixture
def concurrent_clients():
    return 10

def test_system_load(concurrent_clients):
    """Test system handling multiple clients"""
    def client_session():
        client_id = str(uuid.uuid4())
        requests.post(f"http://localhost:5000/register", 
                     json={"client_id": client_id, "subscriber": "subscriber_topic_1"})
        
        for _ in range(100):
            data = {
                "user_id": client_id,
                "emoji_type": "😀",
                "timestamp": datetime.now().isoformat()
            }
            requests.post("http://localhost:5000/emoji", json=data)
            time.sleep(0.01)
    
    with ThreadPoolExecutor(max_workers=concurrent_clients) as executor:
        futures = [executor.submit(client_session) for _ in range(concurrent_clients)]
        for future in futures:
            future.result()

if __name__ == '__main__':
    unittest.main()