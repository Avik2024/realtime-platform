-- timescale-init/init.sql

-- This script will run automatically the first time the database starts.

-- Step 1: Create a standard PostgreSQL table to hold the alert data.
-- We define columns that match the JSON data coming from our Kafka alert topic.
CREATE TABLE alerts (
    ts              TIMESTAMPTZ     NOT NULL, -- The timestamp of the event (timezone aware)
    level           VARCHAR(50),              -- e.g., 'CRITICAL'
    reason          VARCHAR(100),             -- e.g., 'HIGH_TEMPERATURE'
    sensor_id       VARCHAR(50),              -- e.g., 'sensor-001'
    temperature_c   DECIMAL,                  -- The actual temperature reading
    threshold_c     DECIMAL,                  -- The threshold that was breached
    source_offset   BIGINT                    -- The offset of the original message in the source Kafka topic
);

-- Step 2: This is the magic of TimescaleDB.
-- We use the create_hypertable() function to convert our regular 'alerts' table
-- into a hypertable. This automatically partitions the data by time ('ts' column),
-- which is the key to TimescaleDB's high performance for time-series data.
SELECT create_hypertable('alerts', 'ts');