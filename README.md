# Getting Started with FASTAPI and PostgreSQL

This guide will walk you through the basic setup to get started with FASTAPI, a modern web framework for building APIs with Python, along with PostgreSQL database integration using psycopg2-binary.

## Prerequisites

- Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- PostgreSQL installed and running on your system. You can download it from [postgresql.org](https://www.postgresql.org/download/).

## Installation

1. **Install FASTAPI**:

    ```bash
    pip install fastapi
    ```

2. **Install Uvicorn** (ASGI server):

    ```bash
    pip install uvicorn
    ```

3. **Install psycopg2-binary** (PostgreSQL adapter for Python):

    ```bash
    pip install psycopg2-binary
    ```

    **Note**: psycopg2-binary is required to work with PostgreSQL in Python. It provides a way to interact with PostgreSQL databases from Python code.

## Usage

1. **Create a FASTAPI app**:

    Create a new Python file (e.g., `main.py`) and import necessary modules:

    ```python
    from fastapi import FastAPI

    app = FastAPI()
    ```

2. **Run the app with Uvicorn**:

    ```bash
    uvicorn main:app --reload
    ```

    This command will start the ASGI server and reload the server automatically when code changes are detected.

3. **Connect to PostgreSQL**:

    Before using PostgreSQL with FASTAPI, make sure you have a PostgreSQL server running and you know the connection details (e.g., host, port, username, password).

    You can establish a connection to PostgreSQL using psycopg2-binary:

    ```python
    import psycopg2

    # Establish connection
    connection = psycopg2.connect(
        dbname="your_database",
        user="your_username",
        password="your_password",
        host="localhost",
        port="5432"
    )

    # Create a cursor object
    cursor = connection.cursor()

    # Execute SQL queries
    cursor.execute("SELECT * FROM your_table")

    # Fetch data
    rows = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    connection.close()
    ```

    Replace `"your_database"`, `"your_username"`, `"your_password"`, `"localhost"`, and `"5432"` with your actual PostgreSQL database details.

## Conclusion

You've now set up a basic environment to work with FASTAPI and PostgreSQL using psycopg2-binary. Feel free to explore more features of FASTAPI and customize your application as needed.

---

# Integrating JWT Authentication with FASTAPI

This guide will show you how to integrate JWT (JSON Web Tokens) authentication with FASTAPI, a modern web framework for building APIs with Python.

## Prerequisites

- Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- Understanding of basic Python concepts and web development principles.

## Usage

1. **Install PyJWT** (JWT implementation for Python):

    ```bash
    pip install pyjwt
    ```

2. **Generate JWT Tokens**:

    Use PyJWT to generate and verify JWT tokens in your FASTAPI application. Here's a basic example:

    ```python
    import jwt

    # Secret key for encoding and decoding tokens
    SECRET_KEY = "your_secret_key"

    # Encode JWT token
    def create_jwt_token(data):
        return jwt.encode(data, SECRET_KEY, algorithm="HS256")

    # Decode JWT token
    def decode_jwt_token(token):
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    ```

3. **Protect Routes with JWT Authentication**:

    Use JWT tokens to protect specific routes in your FASTAPI app by verifying the token in request headers. Here's a basic example:

    ```python
    from fastapi import FastAPI, HTTPException, Depends
    from pydantic import BaseModel
    from typing import Optional
    from .jwt_utils import decode_jwt_token

    app = FastAPI()

    # Example protected route
    @app.get("/protected_route")
    async def protected_route(token: Optional[str] = Depends(decode_jwt_token)):
        # Token verification successful, proceed with protected logic
        return {"message": "Access granted"}

    # Example login route that generates JWT token
    @app.post("/login")
    async def login(username: str, password: str):
        # Check username and password, generate JWT token if valid
        token = create_jwt_token({"username": username})
        return {"token": token}
    ```

    In this example, the `protected_route` is protected by the `decode_jwt_token` dependency, which verifies the JWT token present in the request headers.

## Conclusion

You've now integrated JWT authentication with FASTAPI using PyJWT. Feel free to explore more features of JWT and customize your authentication logic as needed.

---

Below is the revised guide for using environment variables with FASTAPI and the python-dotenv library, excluding the installation steps for FASTAPI and Uvicorn:

---

# Using Environment Variables with FASTAPI and python-dotenv

This guide will demonstrate how to use environment variables with FASTAPI and the python-dotenv library, allowing you to load environment variables from a .env file.

## Prerequisites

- Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- Understanding of basic Python concepts and web development principles.

## Usage

1. **Install python-dotenv** (library for managing environment variables):

    ```bash
    pip install python-dotenv
    ```

2. **Create a .env file**:

    Create a file named `.env` in your project directory and define your environment variables in the following format:

    ```plaintext
    SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url
    ```

    Replace `your_secret_key` and `your_database_url` with your actual values.

3. **Load Environment Variables**:

    Use python-dotenv to load environment variables from the .env file in your FASTAPI application. Here's an example:

    ```python
    from fastapi import FastAPI
    from dotenv import load_dotenv
    import os

    # Load environment variables from .env file
    load_dotenv()

    # Access environment variables
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")

    app = FastAPI()

    # Example route using environment variables
    @app.get("/")
    async def read_root():
        return {"secret_key": SECRET_KEY, "database_url": DATABASE_URL}
    ```

4. **Run your FASTAPI app**:

    Start your FASTAPI application using Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

    Replace `main` with the name of your Python file containing the FASTAPI app.

## Conclusion

You've now learned how to use environment variables with FASTAPI and python-dotenv. This allows you to securely manage sensitive information and configuration settings for your application.

---