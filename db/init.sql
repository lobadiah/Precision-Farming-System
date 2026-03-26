CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer'
);

CREATE TABLE IF NOT EXISTS farms (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    crop_type VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER REFERENCES farms(id),
    zone_id VARCHAR(100) NOT NULL,
    mac_address VARCHAR(50) UNIQUE,
    activation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    zone_id VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- 'WATER' or 'FERTILIZER'
    suggested_amount DECIMAL(10,2),
    reasoning_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'PENDING'
);

-- Insert dummy data for MVP
INSERT INTO users (email, password_hash, role) VALUES ('admin@farm.local', 'hashed_pass_placeholder', 'admin');
INSERT INTO farms (owner_id, name, latitude, longitude, crop_type) VALUES (1, 'Green Acres', 34.0522, -118.2437, 'Corn');
INSERT INTO devices (farm_id, zone_id, mac_address) VALUES (1, 'Zone_A', '00:1B:44:11:3A:B7');
