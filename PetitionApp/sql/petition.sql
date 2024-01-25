CREATE TABLE petition (
    ID SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    petition_name VARCHAR(255) NOT NULL,
    petition_text TEXT NOT NULL,
    images BYTEA
);