import os
os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import pytest
from httpx import AsyncClient
from src.main import app
from src.database import Base, engine
import asyncio
import sqlalchemy
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Use a test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://formuser:formpass@db:5432/formdb")

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_and_get_submission():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone_number": "1234567890",
            "age": 30,
            "address": "123 Main St",
            "preferred_contact": "Email"
        }
        # Create
        resp = await ac.post("/api/submissions/", json=data)
        assert resp.status_code == 201
        result = resp.json()
        assert result["full_name"] == data["full_name"]
        submission_id = result["id"]
        # Get
        resp = await ac.get(f"/api/submissions/{submission_id}")
        assert resp.status_code == 200
        assert resp.json()["email"] == data["email"]

@pytest.mark.asyncio
async def test_list_submissions():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/submissions/")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_list_submissions_pagination_and_search():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create multiple submissions
        for i in range(5):
            await ac.post("/api/submissions/", json={
                "full_name": f"Paginate User {i}",
                "email": f"paginate{i}@example.com",
                "phone_number": f"100000000{i}",
                "age": 20 + i,
                "address": f"{i} Main St",
                "preferred_contact": "Email"
            })
        # Test pagination
        resp = await ac.get("/api/submissions/?skip=0&limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2
        # Test search
        resp = await ac.get("/api/submissions/?search=Paginate User 1")
        assert resp.status_code == 200
        data = resp.json()
        assert any("Paginate User 1" in item["full_name"] for item in data["items"])

@pytest.mark.asyncio
async def test_duplicate_email_create():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {
            "full_name": "Dup Email",
            "email": "dup@example.com",
            "phone_number": "1231231234",
            "age": 30,
            "address": "Dup St",
            "preferred_contact": "Email"
        }
        resp1 = await ac.post("/api/submissions/", json=data)
        assert resp1.status_code == 201
        resp2 = await ac.post("/api/submissions/", json=data)
        assert resp2.status_code == 400
        assert "Duplicate email" in str(resp2.json())

@pytest.mark.asyncio
async def test_duplicate_email_update():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create two submissions
        data1 = {
            "full_name": "User One",
            "email": "userone@example.com",
            "phone_number": "1111111111",
            "age": 22,
            "address": "One St",
            "preferred_contact": "Email"
        }
        data2 = {
            "full_name": "User Two",
            "email": "usertwo@example.com",
            "phone_number": "2222222222",
            "age": 23,
            "address": "Two St",
            "preferred_contact": "Phone"
        }
        resp1 = await ac.post("/api/submissions/", json=data1)
        id1 = resp1.json()["id"]
        resp2 = await ac.post("/api/submissions/", json=data2)
        id2 = resp2.json()["id"]
        # Try to update user two to have user one's email
        update_data = data2.copy()
        update_data["email"] = data1["email"]
        resp = await ac.put(f"/api/submissions/{id2}", json=update_data)
        assert resp.status_code == 400
        assert "Duplicate email" in str(resp.json())

@pytest.mark.asyncio
async def test_update_validation_errors():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a valid submission
        data = {
            "full_name": "Valid User",
            "email": "validuser@example.com",
            "phone_number": "3333333333",
            "age": 30,
            "address": "Valid St",
            "preferred_contact": "Both"
        }
        resp = await ac.post("/api/submissions/", json=data)
        submission_id = resp.json()["id"]
        # Try to update with invalid data
        update_data = data.copy()
        update_data["age"] = 10  # Invalid age
        update_data["preferred_contact"] = "Invalid"
        resp = await ac.put(f"/api/submissions/{submission_id}", json=update_data)
        assert resp.status_code == 422

@pytest.mark.asyncio
async def test_update_submission():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create
        data = {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "phone_number": "0987654321",
            "age": 25,
            "address": "456 Main St",
            "preferred_contact": "Phone"
        }
        resp = await ac.post("/api/submissions/", json=data)
        submission_id = resp.json()["id"]
        # Update
        update_data = data.copy()
        update_data["age"] = 26
        resp = await ac.put(f"/api/submissions/{submission_id}", json=update_data)
        assert resp.status_code == 200
        assert resp.json()["age"] == 26

@pytest.mark.asyncio
async def test_delete_submission():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create
        data = {
            "full_name": "Delete Me",
            "email": "delete@example.com",
            "phone_number": "1112223333",
            "age": 40,
            "address": "789 Main St",
            "preferred_contact": "Both"
        }
        resp = await ac.post("/api/submissions/", json=data)
        submission_id = resp.json()["id"]
        # Delete
        resp = await ac.delete(f"/api/submissions/{submission_id}")
        assert resp.status_code == 204
        # Confirm deletion
        resp = await ac.get(f"/api/submissions/{submission_id}")
        assert resp.status_code == 404

@pytest.mark.asyncio
async def test_validation_errors():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Missing required field
        data = {
            "email": "bad@example.com",
            "phone_number": "1234567890",
            "age": 17,
            "preferred_contact": "Invalid"
        }
        resp = await ac.post("/api/submissions/", json=data)
        assert resp.status_code == 422 