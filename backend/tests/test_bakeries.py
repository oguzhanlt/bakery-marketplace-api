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


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "backend running"}

def test_get_all_bakeries():
    response0 = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test123@test.com",
            "password": "123456",
            "role": "bakery_owner"
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
            "Authorization": f"Bearer {token}"
        }
    )

    response = client.get("/bakeries")
    db = TestingSessionLocal()
    bakeries = db.query(Bakery).all()
    db.close()

    assert response0.status_code == 200
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response.status_code == 200
    #print([(bakery.name, bakery.description, bakery.location) for bakery in bakeries])
    assert len(bakeries) == 1

def test_create_bakery_as_owner():
    response0 = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test123@test.com",
            "password": "123456",
            "role": "bakery_owner"
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
            "Authorization": f"Bearer {token}"
        }
    )

    assert response0.status_code == 200
    assert response1.status_code == 200
    assert response2.status_code == 200


def test_create_bakery_as_customer_forbidden():
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
            "Authorization": f"Bearer {token}"
        }
    )

    assert response0.status_code == 200
    assert response1.status_code == 200
    assert response2.status_code == 403

def test_create_bakery_unauthorized():
    response = client.post(
        "/bakery",
        json={
            "name": "Test Bakery",
            "description": "A test bakery",
            "location": "Test Location"
        }
    )

    assert response.status_code == 401

def test_create_bakery_invalid_token():
    response = client.post(
        "/bakery",
        json={
            "name": "Test Bakery",
            "description": "A test bakery",
            "location": "Test Location"
        },
        headers={
            "Authorization": f"some invalidtoken"
        }
    )

    assert response.status_code == 401