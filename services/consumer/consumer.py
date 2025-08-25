import json
import os
import time
from kafka import KafkaConsumer, KafkaProducer

# --- Kafka Configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "sensor.temperatures")
ALERT_TOPIC = os.getenv("ALERT_TOPIC", "alerts.high-temp")
GROUP_ID = os.getenv("GROUP_ID", "temp-processor")
TEMP_THRESHOLD_C = float(os.getenv("TEMP_THRESHOLD_C", "50"))


# --- Function to create Kafka Consumer with retry logic ---
def create_kafka_consumer():
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                auto_offset_reset="earliest",
            )
            print("[consumer] Successfully connected to Kafka.")
        except Exception as e:
            print(f"[consumer] Could not connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    return consumer


# --- Function to create Kafka Producer with retry logic ---
def create_kafka_producer():
    producer = None
    while producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda v: v.encode("utf-8") if v else None,
            )
            print("[producer] Successfully connected to Kafka.")
        except Exception as e:
            print(f"[producer] Could not connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    return producer


# --- Main Logic ---
def main():
    consumer = create_kafka_consumer()
    producer = create_kafka_producer()

    print(f"[consumer] Reading from {INPUT_TOPIC}; alert if temp > {TEMP_THRESHOLD_C}C -> {ALERT_TOPIC}")

    for msg in consumer:
        try:
            record = msg.value
            sensor_id = record.get("sensor_id")
            temp = float(record.get("temperature_c", -1))

            if temp > TEMP_THRESHOLD_C:
                alert = {
                    "ts": record.get("ts"),
                    "level": "CRITICAL",
                    "reason": "HIGH_TEMPERATURE",
                    "sensor_id": sensor_id,
                    "temperature_c": temp,
                    "threshold_c": TEMP_THRESHOLD_C,
                    "source_offset": msg.offset,
                }
                producer.send(ALERT_TOPIC, key=sensor_id, value=alert)
                producer.flush()
                print(f"[ALERT->published] {alert}")
            else:
                print(f"[consumer] OK sensor={sensor_id} temp={temp}C")
        except Exception as e:
            print(f"[consumer] Error processing message: {e}")


if __name__ == "__main__":
    main()