CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE,
    email VARCHAR UNIQUE,
    first_name VARCHAR,
    last_name VARCHAR,
    hashed_password VARCHAR,
    is_activate BOOLEAN DEFAULT TRUE,
    role VARCHAR
);

