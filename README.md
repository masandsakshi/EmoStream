# 🚀 Emostream: Real-Time Emoji Broadcasting with Event-Driven Architecture

# 📌 Overview

Emostream is a high-performance, real-time emoji streaming platform designed to deliver concurrent emoji broadcasts efficiently using Apache Kafka, Apache Spark, and Python. The system leverages an event-driven architecture to ensure seamless data aggregation and processing while maintaining scalability and fault tolerance.

# 📌 Key Features

Real-Time Data Streaming: Utilizes Apache Kafka for message brokering and Apache Spark for high-speed stream processing.

Scalable & Distributed: Built with horizontal scalability in mind, handling multiple Kafka topics and consumer groups.

Efficient Data Aggregation: Spark Streaming jobs process and aggregate emoji events dynamically.

Event-Driven System: Decoupled services ensure optimized performance and better fault isolation.

Load Testing & Monitoring: Integrated with Locust for performance evaluation and Pytest for unit testing.

# 📌 Prerequisites

Ensure the following dependencies are installed before running the project:

Apache Kafka (for event streaming)

Apache Spark (for real-time stream processing)

Conda (for virtual environment management)

Python 3 (core programming language)

Locust (for load testing)

Pytest (for unit testing)

# 📌 Quickstart Guide

1.  Start Zookeeper & Kafka Server

cd /etc/systemd/system/
sudo systemctl stop zookeeper

cd /usr/local/kafka
sudo bin/kafka-server-start.sh config/server.properties
sudo bin/zookeeper-server-start.sh config/zookeeper.properties

2️. Create Kafka Topics

cd /usr/local/kafka
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic emoji_topic --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic emoji_topic_aggregated --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic cluster_topic_1 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic cluster_topic_2 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic cluster_topic_3 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic subscriber_topic_1 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic subscriber_topic_2 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic subscriber_topic_3 --partitions 3 --replication-factor 1

3️. Launch the Spark Streaming Job

conda activate bd
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 emoji_aggregator_new.py

4️. Start Backend Microservices

conda activate bd
python3 app_new.py  # Main API service
python3 main_publisher.py  # Central event publisher
python3 cluster_publisher_1.py  # Clustered publisher instance 1
python3 cluster_publisher_2.py  # Clustered publisher instance 2
python3 cluster_publisher_3.py  # Clustered publisher instance 3
python3 dynamic_client_manager.py  # Manages client subscriptions dynamically
python3 aggregation_viewer.py  # Visualization of aggregated data
python3 emo_stream_server.py  # WebSocket server for emoji broadcasting

5️. Access the Frontend Dashboard

Visit the live interface at:

http://localhost:5001

6️. Run Tests

# 📌 Unit Tests

python -m pytest test_emoji.py -v

# 📌  Load Testing with Locust

locust -f test_emoji.py --host=http://localhost:5000 --users 100 --spawn-rate 10

📌 Additional Notes

Ensure all required services (Kafka, Spark, and backend services) are running before executing the scripts.

Modify configurations as needed in the Kafka and Spark settings to match your infrastructure.

The system is designed to scale horizontally—Kafka partitions and Spark consumers can be increased for handling higher loads.
