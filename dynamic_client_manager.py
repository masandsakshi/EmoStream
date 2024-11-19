# dynamic_client_manager.py
import requests
import random
import time
import uuid
import signal
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
from tabulate import tabulate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicClient:
    def __init__(self, client_id, subscriber_topic):
        self.client_id = client_id
        self.subscriber_topic = subscriber_topic
        self.emojis = ['😀', '😂', '🥰', '😢', '😡']
        self.running = True
        self.active = False
        self.last_heartbeat = datetime.now()
    
    def register(self):
        try:
            response = requests.post('http://localhost:5000/register', 
                                   json={"client_id": self.client_id, 
                                        "subscriber": self.subscriber_topic})
            self.active = response.status_code == 200
            return self.active
        except:
            return False
    
    def deregister(self):
        try:
            response = requests.post('http://localhost:5000/deregister', 
                                   json={"client_id": self.client_id})
            self.active = False
            return response.status_code == 200
        except:
            return False
    
    def send_emojis(self):
        while self.running:
            if self.active:
                data = {
                    "user_id": self.client_id,
                    "emoji_type": random.choice(self.emojis),
                    "timestamp": datetime.now().isoformat()
                }
                try:
                    requests.post('http://localhost:5000/emoji', json=data)
                    self.last_heartbeat = datetime.now()
                    time.sleep(0.01)
                except:
                    self.active = False
            else:
                time.sleep(1)
                self.register()

class ClientManager:
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()
        self.running = True
        self.subscriber_topics = [
            'subscriber_topic_1',
            'subscriber_topic_2',
            'subscriber_topic_3'
        ]
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def add_client(self):
        client_id = str(uuid.uuid4())
        topic = random.choice(self.subscriber_topics)
        client = DynamicClient(client_id, topic)
        
        with self.lock:
            self.clients[client_id] = client
        
        if client.register():
            thread = threading.Thread(target=client.send_emojis)
            thread.daemon = True
            thread.start()
            logger.info(f"Added client {client_id} to {topic}")
        return client_id
    
    def remove_client(self, client_id):
        with self.lock:
            if client_id in self.clients:
                client = self.clients[client_id]
                client.running = False
                client.deregister()
                del self.clients[client_id]
                logger.info(f"Removed client {client_id}")
    
    def monitor_clients(self):
        while self.running:
            with self.lock:
                current_time = datetime.now()
                inactive_clients = [
                    cid for cid, client in self.clients.items()
                    if (current_time - client.last_heartbeat).seconds > 5
                ]
                
                for client_id in inactive_clients:
                    self.remove_client(client_id)
            
            self.display_status()
            time.sleep(1)
    
    def display_status(self):
        with self.lock:
            headers = ['Client ID', 'Topic', 'Status', 'Last Heartbeat']
            table = [
                [cid, client.subscriber_topic,
                 'Active' if client.active else 'Inactive',
                 client.last_heartbeat.strftime('%H:%M:%S')]
                for cid, client in self.clients.items()
            ]
            
            print("\033[H\033[J")  # Clear screen
            print(tabulate(table, headers=headers, tablefmt='grid'))
    
    def handle_shutdown(self, signum, frame):
        logger.info("Shutting down client manager...")
        self.running = False
        with self.lock:
            for client_id in list(self.clients.keys()):
                self.remove_client(client_id)
        sys.exit(0)
    
    def run(self):
        monitor_thread = threading.Thread(target=self.monitor_clients)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        while self.running:
            command = input("\nCommands: (a)dd client, (r)emove client, (q)uit: ").lower()
            if command == 'a':
                self.add_client()
            elif command == 'r':
                if self.clients:
                    client_id = random.choice(list(self.clients.keys()))
                    self.remove_client(client_id)
            elif command == 'q':
                self.handle_shutdown(None, None)

if __name__ == "__main__":
    manager = ClientManager()
    manager.run()