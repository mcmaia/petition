CREATE TABLE signature (
    ID SERIAL PRIMARY KEY,
    petition_id INTEGER REFERENCES petition(ID),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    show_signature BOOLEAN NOT NULL
);