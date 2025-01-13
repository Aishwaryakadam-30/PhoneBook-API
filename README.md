# PhoneBook-API
Overview

The PhoneBook API is a simple application built using FastAPI that allows users to manage a phonebook. It supports operations like adding, listing, and deleting contacts while maintaining a detailed audit log of operations.

# Features

Add new contacts with validation for names and phone numbers.

List all contacts stored in the database.

Delete contacts by name or phone number.

Audit logging for all operations.

SQLite for backend storage.

Built-in unit tests for reliability.

# Prerequisites

Make sure you have the following installed:

Python (>=3.9): Download Python

Docker: Download Docker

Postman (Optional, for testing): Download Postman

# Installation Instructions

Step 1: Clone the Repository

git clone https://github.com/your-username/phonebook-api.git
cd phonebook-api

# Step 2: Set Up the Environment

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

Install the required dependencies:

pip install -r requirements.txt

# Step 3: Run the Application

Start the FastAPI application:

uvicorn app:app --reload

Access the API documentation at http://localhost:8000/docs.

# Step 4: Run Using Docker

Build the Docker image:

docker build -t phonebook-app .

Run the Docker container:

docker run -p 8000:8000 phonebook-app

Access the API at http://localhost:8000/docs.

# Running Unit Tests

Ensure the Docker container is running.

Open a new terminal and execute the tests:

docker exec -it <CONTAINER_ID> pytest test.py

Replace <CONTAINER_ID> with your running container's ID (use docker ps to find it).

# API Endpoints

1. List Contacts

Endpoint: /contacts/list

Method: GET

2. Add a Contact

Endpoint: /contacts/add
Method: POST
Body:
{
  "full_name": "John Doe",
  "contact_number": "1234567890"
}

3. Delete Contact by Name
Endpoint: /contacts/deleteByName
Method: PUT
Query Parameter: contact_name=John Doe

4. Delete Contact by Phone
Endpoint: /contacts/deleteByPhone
Method: PUT
Query Parameter: contact_number=1234567890

Project Structure

phonebook-api/
|-- app.py              # Main FastAPI application
|-- test.py             # Unit tests
|-- requirements.txt    # Python dependencies
|-- Dockerfile          # Docker setup
|-- README.md           # Project documentation

Contributing
Contributions are welcome! Feel free to submit a pull request or report issues.

License
This project is licensed under the MIT License. See LICENSE for more information.

