CREATE TABLE picks(
       event_id TEXT,
       channel_id TEXT,
       trace_start_time DATETIME,
       pick_sample INTEGER,
       created_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
