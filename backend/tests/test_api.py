import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))
# os.environ["DATABASE"] = "sqlite:///:memory:"
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.main import app
from src import auth
from src.database import SessionLocal
from src.models import Submission
from sqlalchemy.exc import IntegrityError

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_not_found():
    response = client.get("/api/doesnotexist")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_protected_route_unauthorized():
    response = client.get("/api/submissions/api/protected")
    assert response.status_code == 401 or response.status_code == 403
    assert "detail" in response.json()

def make_submission_payload(email="test@example.com"):
    return {
        "full_name": "Test User",
        "email": email,
        "phone_number": "+1234567890",
        "age": 30,
        "address": "123 Test St",
        "preferred_contact": "Email"
    }

def test_create_and_crud_submission():
    # Create
    payload = make_submission_payload()
    response = client.post("/api/submissions/", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == payload["email"]
    submission_id = data["id"]

    # Read (list)
    response = client.get("/api/submissions/")
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["id"] == submission_id for item in items)

    # Read (single)
    response = client.get(f"/api/submissions/{submission_id}")
    assert response.status_code == 200
    assert response.json()["id"] == submission_id

    # Update
    update_payload = make_submission_payload(email="updated@example.com")
    response = client.put(f"/api/submissions/{submission_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"

    # Delete
    response = client.delete(f"/api/submissions/{submission_id}")
    assert response.status_code == 204

    # Confirm deletion
    response = client.get(f"/api/submissions/{submission_id}")
    assert response.status_code == 404

# --- AUTH.PY COVERAGE ---