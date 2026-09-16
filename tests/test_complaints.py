import pytest
import pytest_asyncio

from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db

from notification_service import notification_service


# ==================================================
# TEST DATABASE
# ==================================================

TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
)


# ==================================================
# OVERRIDE DATABASE
# ==================================================

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# ==================================================
# TEST DATABASE SETUP
# ==================================================

@pytest_asyncio.fixture(autouse=True)
async def setup_database():

    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )


# ==================================================
# TEST CLIENT
# ==================================================

@pytest.fixture
def client():

    return TestClient(app)


# ==================================================
# SIGNUP
# ==================================================

def test_signup(client):

    response = client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "password123",
            "name": "Student One",
            "email": "student1@test.com",
            "room_number": "A101"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Account created successfully"
    assert data["username"] == "student1"


# ==================================================
# DUPLICATE USERNAME
# ==================================================

def test_duplicate_username(client):

    client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "password123",
            "name": "Student One",
            "email": "student1@test.com",
            "room_number": "A101"
        }
    )

    response = client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "different",
            "name": "Student Two",
            "email": "student2@test.com",
            "room_number": "B202"
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Username already exists"
    )


# ==================================================
# LOGIN
# ==================================================

def test_login(client):

    client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "password123",
            "name": "Student One",
            "email": "student1@test.com",
            "room_number": "A101"
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "student1",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ==================================================
# INVALID LOGIN
# ==================================================

def test_invalid_login(client):

    client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "password123",
            "name": "Student One",
            "email": "student1@test.com",
            "room_number": "A101"
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "student1",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid username or password"
    )


# ==================================================
# CREATE COMPLAINT
# ==================================================

def test_create_complaint(client):

    # Signup
    client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "password123",
            "name": "Student One",
            "email": "student1@test.com",
            "room_number": "A101"
        }
    )

    # Login
    login_response = client.post(
        "/login",
        data={
            "username": "student1",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create complaint
    response = client.post(
        "/complaints",
        headers=headers,
        json={
            "title": "Broken fan",
            "description": "The fan is not working",
            "category": "Electrical"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Broken fan"
    assert data["category"] == "Electrical"
    assert data["status"] == "Pending"


# ==================================================
# UNAUTHORIZED CREATE
# ==================================================

def test_create_complaint_without_login(client):

    response = client.post(
        "/complaints",
        json={
            "title": "Broken fan",
            "description": "The fan is not working",
            "category": "Electrical"
        }
    )

    assert response.status_code == 401


# ==================================================
# AUTHORIZATION REGRESSION
# ==================================================

def test_student_cannot_access_other_students_complaint(
    client
):

    # ------------------------------
    # Student 1 signup
    # ------------------------------

    client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "password123",
            "name": "Student One",
            "email": "student1@test.com",
            "room_number": "A101"
        }
    )

    # ------------------------------
    # Student 1 login
    # ------------------------------

    login_response = client.post(
        "/login",
        data={
            "username": "student1",
            "password": "password123"
        }
    )

    token1 = login_response.json()["access_token"]

    headers1 = {
        "Authorization": f"Bearer {token1}"
    }

    # ------------------------------
    # Student 1 creates complaint
    # ------------------------------

    complaint_response = client.post(
        "/complaints",
        headers=headers1,
        json={
            "title": "Broken fan",
            "description": "Fan is not working",
            "category": "Electrical"
        }
    )

    assert complaint_response.status_code == 201

    complaint_id = complaint_response.json()["id"]

    # ------------------------------
    # Student 2 signup
    # ------------------------------

    client.post(
        "/signup",
        json={
            "username": "student2",
            "password": "password456",
            "name": "Student Two",
            "email": "student2@test.com",
            "room_number": "B202"
        }
    )

    # ------------------------------
    # Student 2 login
    # ------------------------------

    login_response = client.post(
        "/login",
        data={
            "username": "student2",
            "password": "password456"
        }
    )

    token2 = login_response.json()["access_token"]

    headers2 = {
        "Authorization": f"Bearer {token2}"
    }

    # ------------------------------
    # Student 2 tries accessing
    # Student 1's complaint
    # ------------------------------

    response = client.get(
        f"/complaints/{complaint_id}",
        headers=headers2
    )

    assert response.status_code == 404


# ==================================================
# SEARCH / FILTER
# ==================================================

def test_complaint_filter(client):

    # Signup
    client.post(
        "/signup",
        json={
            "username": "student1",
            "password": "password123",
            "name": "Student One",
            "email": "student1@test.com",
            "room_number": "A101"
        }
    )

    # Login
    login_response = client.post(
        "/login",
        data={
            "username": "student1",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create complaint
    client.post(
        "/complaints",
        headers=headers,
        json={
            "title": "Broken fan",
            "description": "Fan is not working",
            "category": "Electrical"
        }
    )

    # Search
    response = client.get(
        "/complaints?search=fan",
        headers=headers
    )

    assert response.status_code == 200

    complaints = response.json()

    assert len(complaints) == 1
    assert complaints[0]["title"] == "Broken fan"


# ==================================================
# NOTIFICATION SERVICE
# ==================================================

@pytest.mark.asyncio
async def test_notification_service():

    result = await notification_service.send_complaint_notification(
        student_email="test@example.com",
        complaint_id=1,
        title="Test complaint"
    )

    assert result is True