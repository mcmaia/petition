CREATE TABLE signature (
    id SERIAL PRIMARY KEY,
    petition_id INTEGER REFERENCES petition(id),
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(50),
    show_signature BOOLEAN,
    can_be_contacted BOOLEAN,
    validated_signature BOOLEAN,
    user_id INTEGER REFERENCES users(id)
);
