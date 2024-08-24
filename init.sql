-- Create 'users' table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password TEXT
);

-- Create 'bills' table
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    session TEXT,
    introduced DATE,
    name TEXT,
    number TEXT,
    home_chamber TEXT,
    law BOOLEAN,
    sponsor_politician_url TEXT,
    sponsor_politician_membership_url TEXT,
    status TEXT
);
