# Real-time Distributed Data Processing & Analytics Platform

This stack launches Kafka (single-node KRaft mode), a Python producer that streams random temperature data, a Python consumer that checks the temperature and emits alerts to a separate topic, and an alert listener that prints the alerts.

## Prerequisites
- Docker & Docker Compose installed

## Quick Start
```bash
# from the repo root
docker compose up --build