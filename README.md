# Real-time Data Platform 🚀

A **real-time data processing and visualization platform** built with **Kafka, TimescaleDB, Grafana, and Docker**.  
This system ingests sensor data, processes it, raises alerts, and visualizes results in Grafana dashboards.

---

## 📂 Architecture Overview
![System Architecture](assets/database_connection.png)

---

## ⚙️ Tech Stack
- **Apache Kafka** – Event streaming backbone
- **TimescaleDB (PostgreSQL extension)** – Time-series database
- **Grafana** – Interactive dashboards and alerting
- **Docker Compose** – Service orchestration
- **Python Microservices** – Data producer, consumer, sink, and alert listener

---

## 📊 Grafana Dashboards
### Realtime Monitoring
![Grafana Dashboard](assets/grafana_dashboard.png)

### Database Metrics
![Grafana Database](assets/grafana_database.png)

### PostgreSQL Integration
![Grafana PostgreSQL](assets/grafana_postgresql.png)

---

## 🔌 Kafka UI
![Kafka UI](assets/kafkaUI.png)

---

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/Avik2024/realtime-platform.git
   cd realtime-platform
