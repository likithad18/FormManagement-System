import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, get_db, SQLALCHEMY_DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

# Use the same DB URL as your app, but make sure it's a test DB!
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

# Helper for consistent payloads
def make_submission_payload(email="test@example.com"):
    return {
        "full_name": "Test User",
        "email": email,
        "phone_number": "+1234567890",
        "age": 30,
        "address": "123 Test St",
        "preferred_contact": "Email"
    }

def test_create_and_get_submission():
    payload = make_submission_payload("john@example.com")
    resp = client.post("/api/submissions/", json=payload)
    assert resp.status_code == 201
    result = resp.json()
    assert result["full_name"] == payload["full_name"]
    submission_id = result["id"]
    # Get
    resp = client.get(f"/api/submissions/{submission_id}")
    assert resp.status_code == 200
    assert resp.json()["email"] == payload["email"]

def test_list_submissions():
    resp = client.get("/api/submissions/")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)

def test_list_submissions_pagination_and_search():
    # Create multiple submissions
    for i in range(5):
        client.post("/api/submissions/", json=make_submission_payload(f"paginate{i}@example.com"))
    # Test pagination
    resp = client.get("/api/submissions/?skip=0&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 2
    # Test search
    resp = client.get("/api/submissions/?search=Test User")
    assert resp.status_code == 200
    data = resp.json()
    assert any("Test User" in item["full_name"] for item in data["items"])

def test_duplicate_email_create():
    payload = make_submission_payload("dup@example.com")
    resp1 = client.post("/api/submissions/", json=payload)
    assert resp1.status_code == 201
    resp2 = client.post("/api/submissions/", json=payload)
    assert resp2.status_code == 400
    assert "Duplicate email" in str(resp2.json())

def test_update_validation_errors():
    payload = make_submission_payload("validuser@example.com")
    resp = client.post("/api/submissions/", json=payload)
    submission_id = resp.json()["id"]
    update_data = payload.copy()
    update_data["age"] = 10  
    update_data["preferred_contact"] = "Invalid"
    resp = client.put(f"/api/submissions/{submission_id}", json=update_data)
    assert resp.status_code == 422

def test_update_submission():
    payload = make_submission_payload("jane@example.com")
    resp = client.post("/api/submissions/", json=payload)
    submission_id = resp.json()["id"]
    # Update
    update_data = payload.copy()
    update_data["age"] = 26
    resp = client.put(f"/api/submissions/{submission_id}", json=update_data)
    assert resp.status_code == 200
    assert resp.json()["age"] == 26

def test_delete_submission():
    payload = make_submission_payload("delete@example.com")
    resp = client.post("/api/submissions/", json=payload)
    submission_id = resp.json()["id"]
    # Delete
    resp = client.delete(f"/api/submissions/{submission_id}")
    assert resp.status_code == 204
    # Confirm deletion
    resp = client.get(f"/api/submissions/{submission_id}")
    assert resp.status_code == 404

def test_validation_errors():
    # Missing required field
    data = {
        "email": "bad@example.com",
        "phone_number": "+1234567890",
        "age": 17,
        "preferred_contact": "Invalid"
    }
    resp = client.post("/api/submissions/", json=data)
    assert resp.status_code == 422
    # print('Ballllllllll',resp.json())
