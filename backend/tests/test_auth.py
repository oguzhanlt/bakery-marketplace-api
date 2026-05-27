import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import app, get_db
from ..models import User, Base, Bakery


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_test_db():
    Base.metadata.drop_all(bind=engine)
    #print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    yield
    #Base.metadata.drop_all(bind=engine)

def test_register_bakery_owner():
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test123@test.com",
            "password": "123456",
            "role": "bakery_owner"
        }
    )

    db = TestingSessionLocal()
    existing_user = db.query(User).filter(User.email == "test123@test.com").first()
    db.close()
    assert response.status_code == 200
    assert existing_user is not None

def test_register_customer():
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test123@test.com",
            "password": "123456",
            "role": "customer"
        }
    )

    db = TestingSessionLocal()
    existing_user = db.query(User).filter(User.email == "test123@test.com").first()
    db.close()
    assert response.status_code == 200
    assert existing_user is not None
    
def test_register_duplicate_email():
    first_response = client.post(
        "/register",
        json={
            "username": "testuser35",
            "email": "test123@test.com",
            "password": "123456",
            "role": "bakery_owner"
        }
    )

    second_response = client.post(
        "/register",
        json={
            "username": "testuser2",
            "email": "test123@test.com",
            "password": "12345678",
            "role": "customer"
        }
    )

    db = TestingSessionLocal()
    users_with_same_email = db.query(User).filter(User.email == "test123@test.com").all()
    user_with_same_email = db.query(User).filter(User.email == "test123@test.com").first()
    db.close()

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert len(users_with_same_email) == 1

def test_login_success():

    response1 = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test123@test.com",
            "password": "123456",
            "role": "bakery_owner"
        }
    )

    response2 = client.post(
        "/login",
        data={
            "username": "test123@test.com",
            "password": "123456"
        }
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert "access_token" not in response1.json()
    assert "access_token" in response2.json()

def test_login_fail():
    response = client.post(
        "/login",
        data={
            "username": "test123@test.com",
            "password": "password"
        }
    )
    assert response.status_code == 401

def test_login_wrong_password():
    response1 = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test123@test.com",
            "password": "correctpassword",
            "role": "bakery_owner"
        }
    )

    response2 = client.post(
        "/login",
        data={
            "username": "test123@test.com",
            "password": "wrongpassword"
        }
    )
    assert response1.status_code == 200
    assert response2.status_code == 401

def test_email_none():
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": None,
            "password": "123456",
            "role": "bakery_owner"
        }
    )
    
    assert response.status_code != 200

def test_invalid_token():
    response0 = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test123@test.com",
            "password": "123456",
            "role": "customer"
        }
    )

    response1 = client.post("/login", data={
        "username": "test123@test.com",
        "password": "123456"
    })

    token = response1.json()["access_token"]

    response2 = client.post(
        "/bakery",
        json={
            "name": "Test Bakery",
            "description": "A test bakery",
            "location": "Test Location"
        },
        headers={
            "Authorization": f"Bearer {token+"make_it_invalid"}"
        }
    )

    assert response0.status_code == 200
    assert response1.status_code == 200
    assert response2.status_code == 401

def test_read_me():

    register_response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "123456",
            "role": "customer"
        }
    )

    login_response = client.post(
        "/login",
        data={
            "username": "test@test.com",
            "password": "123456"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data["email"] == "test@test.com"
    assert data["username"] == "testuser"
    