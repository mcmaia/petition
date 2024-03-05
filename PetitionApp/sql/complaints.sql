CREATE TABLE complaints (
    ID SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(50),
    complaint_type INT,
    complaint_text TEXT
);


