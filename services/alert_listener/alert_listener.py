import json
import os
from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
ALERT_TOPIC = os.getenv("ALERT_TOPIC", "alerts.high-temp")
GROUP_ID = os.getenv("GROUP_ID", "alert-listener")

consumer = KafkaConsumer(
    ALERT_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id=GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    key_deserializer=lambda k: k.decode("utf-8") if k else None,
    enable_auto_commit=True,
    auto_offset_reset="earliest",
)

print(f"[alert-listener] listening for alerts on {ALERT_TOPIC}")

for msg in consumer:
    print(f"[ALERT] key={msg.key} value={msg.value}")