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


CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    bill_id INTEGER REFERENCES bills(id) ON DELETE CASCADE,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create 'polls' table
CREATE TABLE IF NOT EXISTS polls (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    yes_votes INTEGER DEFAULT 0,
    no_votes INTEGER DEFAULT 0
);

-- Create 'user_poll_votes' table
CREATE TABLE IF NOT EXISTS user_poll_votes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    poll_id INTEGER NOT NULL REFERENCES polls(id) ON DELETE CASCADE,
    vote BOOLEAN NOT NULL, 
    UNIQUE (user_id, poll_id)  
);