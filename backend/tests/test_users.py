def test_get_all_users(client):

    response1 = client.post(
        "/register",
        json={
            "username": "testuser1",
            "email": "testuser@example.com",
            "password": "testpassword",
            "role": "customer"
        }
    )

    response = client.get("/users")
    print("this is from get_all_users:", response.json())

    assert response1.status_code == 200
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_existing_user_by_id(client):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "role": "customer"
        }
    )

    response = client.get("/users/1")
    assert response.status_code == 200

def test_get_non_existing_user_by_id(client):
    response = client.get("/users/1")
    assert response.status_code == 404

def test_update_existing_user(client):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "role": "customer"
        }
    )

    response1 = client.put(
        "/users/1",
        json={
            "username": "updateduser",
            "email": "updateduser@example.com",
            "password": "updatedpassword",
            "role": "customer"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response1.status_code == 200
    assert response1.json()["username"] == "updateduser"

def test_update_non_existing_user(client):
    response = client.put(
        "/users/1",
        json={
            "username": "updateduser",
            "email": "updateduser@example.com",
            "password": "testpassword",
            "role": "customer"
        }
    )
    print("this is from update_non_existing_user:", response.json())
    assert response.status_code == 404

def test_delete_existing_user(client):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "role": "customer"
        }
    )

    response1 = client.delete("/users/1")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response1.status_code == 200
    assert response1.json()["message"] == "user deleted"

def test_delete_non_existing_user(client):
    response = client.delete("/users/1")
    assert response.status_code == 404
