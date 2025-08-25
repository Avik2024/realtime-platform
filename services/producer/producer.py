import json
import os
import time
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("TOPIC", "sensor.temperatures")
INTERVAL = float(os.getenv("PRODUCE_INTERVAL_SEC", "1.0"))

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda v: v.encode("utf-8") if v else None,
)

sensor_ids = [f"sensor-{i:03d}" for i in range(1, 6)]

print(f"[producer] sending to {TOPIC} via {BOOTSTRAP_SERVERS} every {INTERVAL}s")

while True:
    msg = {
        "sensor_id": random.choice(sensor_ids),
        "temperature_c": round(random.uniform(20.0, 70.0), 2),
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    key = msg["sensor_id"]
    producer.send(TOPIC, key=key, value=msg)
    producer.flush()
    print("[producer]", msg)
    time.sleep(INTERVAL)