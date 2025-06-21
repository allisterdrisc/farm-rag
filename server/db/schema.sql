CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS crop_entries (
    id SERIAL PRIMARY KEY,
    name TEXT,
    detailed_name TEXT,
    total_seed_cost FLOAT,
    pounds_harvested INT,
    total_revenue FLOAT,
    total_profit FLOAT,
    embedding VECTOR(1536)
);
