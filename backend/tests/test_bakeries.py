from backend.models import Bakery

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "backend running"}

def test_get_all_bakeries(client, db):
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
    bakeries = db.query(Bakery).all()
    db.close()
    assert response0.status_code == 200
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response.status_code == 200
    #print([(bakery.name, bakery.description, bakery.location) for bakery in bakeries])
    assert len(bakeries) == 1

def test_create_bakery_as_owner(client):
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


def test_create_bakery_as_customer_forbidden(client):
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

def test_create_bakery_unauthorized(client):
    response = client.post(
        "/bakery",
        json={
            "name": "Test Bakery",
            "description": "A test bakery",
            "location": "Test Location"
        }
    )

    assert response.status_code == 401

def test_create_bakery_invalid_token(client):
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

def test_create_bakery_no_token(client):
    response = client.post(
        "/bakery",
        json={
            "name": "Test Bakery",
            "description": "A test bakery",
            "location": "Test Location"
        }
    )

    assert response.status_code == 401

def test_create_bakery_expired_token(client):
    pass

def test_create_bakery_invalid_role(client):
    response = client.post(
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
        })
    
    assert response.status_code == 200
    assert response1.status_code == 200
    assert response2.status_code == 403