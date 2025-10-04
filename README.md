Job Order Tracking System with Kafka, Debezium CDC, and Streamlit
# 🧾 Job Order Tracking System with Kafka, Debezium CDC, and Streamlit

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Apache Kafka](https://img.shields.io/badge/Apache-Kafka-000?logo=apachekafka)
![Debezium CDC](https://img.shields.io/badge/Debezium-CDC-000?logo=debezium)
![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit)

---

## 🏗️ Architecture

Database (MySQL/PostgreSQL) 
    ↓
Debezium Connector (CDC)
    ↓
Apache Kafka (Message Broker)
    ↓
Stream Processing (Kafka Streams/Spark)
    ↓
Streamlit Dashboard (Real-time UI)


## 🛠️ Technologies Used

| Technology | Purpose |
|-------------|----------|
| **Apache Kafka** | Message streaming and event processing |
| **Debezium** | Change Data Capture (CDC) from source databases |
| **Streamlit** | Interactive real-time web dashboard |
| **MySQL / PostgreSQL** | Source databases for job orders |
| **Docker** | Containerization for simplified deployment and scalability |
| **Python** | Backend logic, stream consumer, and data transformation |


## Video Demonstration

🎥 [Watch the demo video](./debezium-project.mp4)
