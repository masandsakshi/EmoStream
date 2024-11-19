from kafka import KafkaConsumer
import json
import threading
from collections import defaultdict
import time
from tabulate import tabulate

class AggregationViewer:
    def __init__(self):
        self.topics = [
            'subscriber_topic_1',
            'subscriber_topic_2',
            'subscriber_topic_3'
        ]
        self.aggregated_data = defaultdict(lambda: defaultdict(int))
        self.lock = threading.Lock()
    
    def consume_topic(self, topic):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id=f'viewer_{topic}'
        )
        
        for message in consumer:
            data = message.value
            with self.lock:
                self.aggregated_data[topic][data['emoji_type']] = data['final_count']
    
    def display_results(self):
        while True:
            with self.lock:
                headers = ['Topic'] + list(set(emoji for d in self.aggregated_data.values() for emoji in d.keys()))
                table = []
                for topic in self.topics:
                    row = [topic]
                    for emoji in headers[1:]:
                        row.append(self.aggregated_data[topic].get(emoji, 0))
                    table.append(row)
                
                print("\033[H\033[J")  # Clear screen
                print(tabulate(table, headers=headers, tablefmt='grid'))
            time.sleep(1)
    
    def run(self):
        threads = []
        for topic in self.topics:
            t = threading.Thread(target=self.consume_topic, args=(topic,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        display_thread = threading.Thread(target=self.display_results)
        display_thread.daemon = True
        display_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    viewer = AggregationViewer()
    viewer.run()