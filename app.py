# Import the required modules
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import re

# Initialize FastAPI application
app = FastAPI()

# SQLite database setup for PhoneBook and AuditLog
contact_db_engine = create_engine("sqlite:///contacts.db", echo=True)
log_db_engine = create_engine("sqlite:///logs.db", echo=True)

# Base models for each database
ContactDBBase = declarative_base()
LogDBBase = declarative_base()

# Contact model class
class ContactEntryModel(ContactDBBase):
    __tablename__ = "contact_entries"

    entry_id = Column(Integer, primary_key=True)
    full_name = Column(String)
    contact_number = Column(String)

# Log model class
class LogEventModel(LogDBBase):
    __tablename__ = "log_events"

    log_id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, index=True)
    event_details = Column(String)
    log_timestamp = Column(DateTime, default=datetime.utcnow)

# Database schema creation
ContactDBBase.metadata.create_all(contact_db_engine)
LogDBBase.metadata.create_all(log_db_engine)

# Session creation for each database
ContactDBSession = sessionmaker(bind=contact_db_engine)
LogDBSession = sessionmaker(bind=log_db_engine)

# Helper functions for validation
def validate_full_name(name):
    if not re.match("^[a-zA-Z(')?\-]+(,)?(\s)?([a-zA-Z\-]+(')?[a-zA-Z\-]+)?(\s)?([a-zA-Z'\-]+)?(.)?$", name):
        return False
    if re.match(".*''.*", name) or re.match(".*\-.*\-.*", name):
        return False
    return True

def validate_contact_number(contact_number):
    patterns = [
        r"^\d{10}$",
        r"^\d{3}-\d{3}-\d{4}$",
        r"^\(\d{3}\) \d{3}-\d{4}$",
        r"^\+\d{1,3} \(\d{1,3}\) \d{3}-\d{4}$"
    ]
    return any(re.match(pattern, contact_number) for pattern in patterns)

# Pydantic model for request data
class ContactPayload(BaseModel):
    full_name: str
    contact_number: str

# Logging function
def record_log_event(log_session, event_name, event_details):
    log_entry = LogEventModel(event_name=event_name, event_details=event_details)
    log_session.add(log_entry)
    log_session.commit()

# API endpoint to list all contacts
@app.get("/contacts/list")
def list_all_contacts():
    contact_session = ContactDBSession()
    all_contacts = contact_session.query(ContactEntryModel).all()
    contact_session.close()
    return all_contacts

# API endpoint to add a new contact
@app.post("/contacts/add")
def add_new_contact(contact: ContactPayload):
    contact_session = ContactDBSession()

    # Validate name and phone number
    if not validate_full_name(contact.full_name):
        contact_session.close()
        raise HTTPException(status_code=400, detail="Invalid full name")
    if not validate_contact_number(contact.contact_number):
        contact_session.close()
        raise HTTPException(status_code=400, detail="Invalid contact number")

    # Check for existing contact
    if contact_session.query(ContactEntryModel).filter_by(contact_number=contact.contact_number).first():
        contact_session.close()
        raise HTTPException(status_code=400, detail="Contact already exists")

    # Add new contact
    new_contact_entry = ContactEntryModel(full_name=contact.full_name, contact_number=contact.contact_number)
    contact_session.add(new_contact_entry)
    contact_session.commit()

    # Record the log event
    record_log_event(LogDBSession(), "add_contact", f"full_name={contact.full_name}, contact_number={contact.contact_number}")
    contact_session.close()
    return {"message": "Contact added successfully"}

# API endpoint to delete contact by name
@app.put("/contacts/deleteByName")
def delete_contact_by_name(contact_name: str):
    if not validate_full_name(contact_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name")
    
    contact_session = ContactDBSession()
    contact_entry = contact_session.query(ContactEntryModel).filter_by(full_name=contact_name).first()
    
    if not contact_entry:
        contact_session.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact_session.delete(contact_entry)
    contact_session.commit()
    record_log_event(LogDBSession(), "delete_contact_by_name", f"full_name={contact_name}")
    contact_session.close()
    return {"message": "Contact deleted successfully"}

# API endpoint to delete contact by phone
@app.put("/contacts/deleteByPhone")
def delete_contact_by_phone(contact_number: str):
    if not validate_contact_number(contact_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contact number")

    contact_session = ContactDBSession()
    contact_entry = contact_session.query(ContactEntryModel).filter_by(contact_number=contact_number).first()

    if not contact_entry:
        contact_session.close()
        raise HTTPException(status_code=404, detail="Contact not found")

    contact_session.delete(contact_entry)
    contact_session.commit()
    record_log_event(LogDBSession(), "delete_contact_by_phone", f"contact_number={contact_number}")
    contact_session.close()
    return {"message": "Contact deleted successfully"}
