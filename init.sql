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
    status TEXT,
    pdf_url TEXT,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
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



CREATE TABLE IF NOT EXISTS bills_bill (
    id SERIAL PRIMARY KEY,
    name_en TEXT NOT NULL,
    number VARCHAR(10) NOT NULL,
    number_only SMALLINT NOT NULL,
    sponsor_member_id INTEGER,
    privatemember BOOLEAN,
    sponsor_politician_id INTEGER,
    law BOOLEAN,
    added DATE NOT NULL,
    institution VARCHAR(1) NOT NULL,
    name_fr TEXT NOT NULL,
    short_title_en TEXT NOT NULL,
    short_title_fr TEXT NOT NULL,
    status_date DATE,
    introduced DATE,
    text_docid INTEGER,
    status_code VARCHAR(50) NOT NULL
);

-- Add indexes for optimization
CREATE INDEX IF NOT EXISTS bills_bill_added ON bills_bill (added);
CREATE INDEX IF NOT EXISTS bills_bill_institution ON bills_bill (institution);
CREATE INDEX IF NOT EXISTS bills_bill_institution_like ON bills_bill (institution varchar_pattern_ops);
CREATE INDEX IF NOT EXISTS bills_bill_sponsor_member_id ON bills_bill (sponsor_member_id);
CREATE INDEX IF NOT EXISTS bills_bill_sponsor_politician_id ON bills_bill (sponsor_politician_id);


CREATE TABLE IF NOT EXISTS bills_billtext (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER NOT NULL REFERENCES bills_bill(id) DEFERRABLE INITIALLY DEFERRED,
    docid INTEGER NOT NULL,
    created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    text_en TEXT NOT NULL,
    text_fr TEXT NOT NULL,
    summary_en TEXT NOT NULL
);

-- Add indexes for optimization
CREATE INDEX IF NOT EXISTS bills_billtext_bill_id ON bills_billtext (bill_id);
CREATE INDEX IF NOT EXISTS bills_billtext_docid ON bills_billtext (docid);

-- Add a unique constraint on docid
ALTER TABLE bills_billtext ADD CONSTRAINT bills_billtext_docid_uniq UNIQUE (docid);

-- Add a check constraint on docid
ALTER TABLE bills_billtext ADD CONSTRAINT bills_billtext_docid_check CHECK (docid >= 0);



-- Create core_party table
CREATE TABLE IF NOT EXISTS core_party (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    slug VARCHAR(10) NOT NULL,
    short_name_en VARCHAR(100) NOT NULL,
    name_fr VARCHAR(100) NOT NULL,
    short_name_fr VARCHAR(100) NOT NULL
);

-- Create core_politician table
CREATE TABLE IF NOT EXISTS core_politician (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_given VARCHAR(50) NOT NULL,
    name_family VARCHAR(50) NOT NULL,
    dob DATE,
    gender VARCHAR(1) NOT NULL,
    headshot VARCHAR(100),
    slug VARCHAR(30) NOT NULL,
    headshot_thumbnail VARCHAR(100)
);

-- Create core_politicianinfo table
CREATE TABLE IF NOT EXISTS core_politicianinfo (
    id SERIAL PRIMARY KEY,
    politician_id INTEGER NOT NULL,
    value TEXT NOT NULL,
    schema VARCHAR(40) NOT NULL,
    created TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_politician FOREIGN KEY (politician_id) REFERENCES core_politician(id) ON DELETE CASCADE
);

-- Indexes for core_party
CREATE INDEX IF NOT EXISTS idx_core_party_name_en ON core_party(name_en);
CREATE INDEX IF NOT EXISTS idx_core_party_slug ON core_party(slug);

-- Indexes for core_politician
CREATE INDEX IF NOT EXISTS idx_core_politician_name ON core_politician(name);
CREATE INDEX IF NOT EXISTS idx_core_politician_slug ON core_politician(slug);

-- Indexes for core_politicianinfo
CREATE INDEX IF NOT EXISTS idx_core_politicianinfo_politician_id ON core_politicianinfo(politician_id);
CREATE INDEX IF NOT EXISTS idx_core_politicianinfo_schema ON core_politicianinfo(schema);
