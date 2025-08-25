import os
import json
import logging
import time
import psycopg2
from kafka import KafkaConsumer
from psycopg2.extras import execute_values

# --- Configuration from environment variables ---
logging.basicConfig(level=logging.INFO, format='[data-sink] %(asctime)s %(levelname)s: %(message)s')

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# --- Function to connect to PostgreSQL with retry logic ---
def connect_to_postgres():
    """Connects to the PostgreSQL database with a retry mechanism."""
    conn = None
    while conn is None:
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            logging.info("Successfully connected to PostgreSQL.")
        except psycopg2.OperationalError as e:
            logging.error(f"Could not connect to PostgreSQL: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    return conn

# --- Function to create Kafka Consumer with retry logic ---
def create_kafka_consumer():
    """Creates a Kafka consumer with a retry mechanism."""
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
                auto_offset_reset='earliest',
                group_id='timescaledb-sink-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logging.info("Successfully connected to Kafka.")
        except Exception as e:
            logging.error(f"Could not connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    return consumer

# --- Main application logic ---
def main():
    """Main function to consume from Kafka and write to TimescaleDB."""
    conn = connect_to_postgres()
    consumer = create_kafka_consumer()
    
    insert_sql = """
        INSERT INTO alerts (ts, level, reason, sensor_id, temperature_c, threshold_c, source_offset)
        VALUES %s
    """

    logging.info(f"Starting to consume messages from Kafka topic: {KAFKA_TOPIC}")
    try:
        for message in consumer:
            try:
                data = message.value
                
                # Prepare data tuple for insertion
                data_tuple = (
                    data.get('ts'),
                    data.get('level'),
                    data.get('reason'),
                    data.get('sensor_id'),
                    data.get('temperature_c'),
                    data.get('threshold_c'),
                    data.get('source_offset')
                )
                
                with conn.cursor() as cursor:
                    execute_values(cursor, insert_sql, [data_tuple])
                    conn.commit()
                
                logging.info(f"Inserted alert for sensor {data.get('sensor_id')} (offset: {message.offset}) into TimescaleDB.")

            except Exception as e:
                logging.error(f"Error processing message: {e}")
                conn.rollback() # Rollback transaction on error
    except KeyboardInterrupt:
        logging.info("Consumer interrupted. Shutting down.")
    finally:
        if consumer:
            consumer.close()
        if conn:
            conn.close()
        logging.info("Kafka consumer and database connection closed.")


if __name__ == "__main__":
    main()