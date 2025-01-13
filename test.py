import json
import pytest
from fastapi.testclient import TestClient
from app import app, ContactDBBase, contact_db_engine

# Create a test client
test_client = TestClient(app)

# Create the tables in the test database
ContactDBBase.metadata.create_all(bind=contact_db_engine)

# Test cases for different scenarios

def test_add_contact():
    response = test_client.post(
        "/contacts/add",
        json={"full_name": "John Doe", "contact_number": "1234567890"}    
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Contact added successfully"

def test_add_contact_invalid_data():
    response = test_client.post(
        "/contacts/add",
        json={"full_name": "<script>alert('XSS')</script>", "contact_number": "invalid"}
    )
    assert response.status_code == 400

def test_delete_contact_by_name():
    # Add a contact to delete later
    test_client.post("/contacts/add", json={"full_name": "Jane Doe", "contact_number": "9876543210"})

    response = test_client.put("/contacts/deleteByName", params={"contact_name": "Jane Doe"})
    assert response.status_code == 200
    assert response.json()["message"] == "Contact deleted successfully"

def test_delete_contact_by_name_not_found():
    response = test_client.put("/contacts/deleteByName", params={"contact_name": "Nonexistent"})
    assert response.status_code == 404

def test_delete_contact_by_number():
    # Add a contact to delete later
    test_client.post("/contacts/add", json={"full_name": "Alice", "contact_number": "5551234567"})

    response = test_client.put("/contacts/deleteByPhone", params={"contact_number": "5551234567"})
    assert response.status_code == 200
    assert response.json()["message"] == "Contact deleted successfully"

def test_delete_contact_by_number_not_found():
    response = test_client.put("/contacts/deleteByPhone", params={"contact_number": "9999999999"})
    assert response.status_code == 404

def test_list_contacts():
    # Add a contact to the contact list for testing listing
    test_client.post("/contacts/add", json={"full_name": "Bob", "contact_number": "1112223333"})

    response = test_client.get("/contacts/list")
    assert response.status_code == 200
    contact_data = response.json()
    assert isinstance(contact_data, list)
    assert any(contact["full_name"] == "Bob" for contact in contact_data)

# Test cases for acceptable names
def test_add_contact_acceptable_names():
    acceptable_names = [
        "Bruce Schneier",
        "Schneier, Bruce",
        "Schneier, Bruce Wayne",
        "O’Malley, John F.",
        "John O’Malley-Smith",
        "Cher"
    ]

    for name in acceptable_names:
        response = test_client.post(
            "/contacts/add",
            json={"full_name": name, "contact_number": "1234567890"}
        )
        print(response.json())
        assert response.status_code == 200
        assert response.json()["message"] == "Contact added successfully"

if __name__ == "__main__":
    pytest.main()
