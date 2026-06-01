import pytest

from backend.tests.conftest import client

@pytest.fixture
def bakery_and_menu(client):
    client.post(
        "/register",
        json={
            "username": "testowner",
            "email": "testowner@example.com",
            "password": "testpassword",
            "role": "bakery_owner"
        }
    )

    response = client.post(
        "/register",
        json={
            "username": "testcustomer",
            "email": "testcustomer@example.com",
            "password": "testpassword",
            "role": "customer"
        }
    )


    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )

    token = login.json()["access_token"]

    bakery = client.post(
        "/bakery",
        json={
            "name": "Test Bakery",
            "description": "A test bakery",
            "location": "Test Location"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    menu_item = client.post(
        "/manage-menu",
        json={
            "bakery_id": bakery.json()["id"],
            "name": "Test Bread",
            "description": "A test bread",
            "price": 3.5
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    logout = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return {
        "owner_token": token,
        "bakery_id": bakery.json()["id"],
        "menu_item_id": menu_item.json()["id"]

    }


def test_get_menu_items_for_bakery(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )

    token = login.json()["access_token"]
    response = client.get(
        f"/bakeries/{bakery_and_menu['bakery_id']}/manage-menu",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Bread"

def test_get_menu_items_for_non_existing_bakery(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )

    token = login.json()["access_token"]
    response = client.get(
        "/bakeries/999/manage-menu",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_owner_adds_menu_item_to_own_bakery(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )

    token = login.json()["access_token"]
    response = client.post(
        "/manage-menu",
        json={
            "bakery_id": bakery_and_menu['bakery_id'],
            "name": "Test Cake",
            "description": "A test Cake",
            "price": 5.5
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_customer_cannot_add_menu_item(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )

    token = login.json()["access_token"]
    response = client.post(
        "/manage-menu",
        json={
            "bakery_id": bakery_and_menu['bakery_id'],
            "name": "Test Cookie",
            "description": "A test Cookie",
            "price": 2.5
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_owner_cannot_add_menu_item_to_other_owner_bakery(client, bakery_and_menu):
    register_another_owner = client.post(
        "/register",
        json={
            "username": "anotherowner",
            "email": "anotherowner@example.com",
            "password": "testpassword",
            "role": "bakery_owner"
        }
    )
    login = client.post(
        "/login",
        data={
            "username": "anotherowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    response = client.post(
        "/manage-menu",
        json={
            "bakery_id": bakery_and_menu['bakery_id'],
            "name": "Test Cookie",
            "description": "A test Cookie",
            "price": 2.5
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_create_menu_item_with_invalid_bakery_id(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    response = client.post(
        "/manage-menu",
        json={
            "bakery_id": 999,
            "name": "Test Cookie",
            "description": "A test Cookie",
            "price": 2.5
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_owner_updates_own_menu_item(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    response = client.patch(
        f"/manage-menu?menu_item_id={bakery_and_menu['menu_item_id']}",
        json={
            "bakery_id": bakery_and_menu['bakery_id'],
            "name": "Updated Test Bread",
            "description": "An updated test Bread",
            "price": 6.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print("this is from test_owner_updates_own_menu_item:", response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Bread"

def test_owner_cannot_update_other_owner_menu_item(client, bakery_and_menu):
    register_another_owner = client.post(
        "/register",
        json={
            "username": "anotherowner",
            "email": "anotherowner@example.com",
            "password": "testpassword",
            "role": "bakery_owner"
        }
    )
    login = client.post(
        "/login",
        data={
            "username": "anotherowner@example.com",
            "password": "testpassword"
        }
    )

    token = login.json()["access_token"]
    response = client.patch(
        f"/manage-menu?menu_item_id={bakery_and_menu['menu_item_id']}",
        json={
            "bakery_id": bakery_and_menu['bakery_id'],
            "name": "Updated Test Bread",
            "description": "An updated test Bread",
            "price": 6.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print("this is from test_owner_cannot_update_other_owner_menu_item:", response.json())
    assert response.status_code == 403

def test_update_non_existing_menu_item(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }    
    )
    token = login.json()["access_token"]
    response = client.patch(
        "/manage-menu?menu_item_id=999",
        json={
            "bakery_id": bakery_and_menu['bakery_id'],
            "name": "Updated Test Bread",
            "description": "An updated test Bread",
            "price": 6.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_update_menu_item_with_invalid_data(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]

    response = client.patch(
        f"/manage-menu?menu_item_id={bakery_and_menu['menu_item_id']}",
        json={
            "bakery_id": bakery_and_menu['bakery_id'],
            "name": "Random Name",
            "description": "An updated test Bread",
            "price": -5.0 # Invalid price
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_owner_deletes_own_menu_item(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    response = client.delete(
        f"/manage-menu?menu_item_id={bakery_and_menu['menu_item_id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_owner_cannot_delete_other_owner_menu_item(client, bakery_and_menu):
    register_another_owner = client.post(
        "/register",
        json={
            "username": "anotherowner",
            "email": "anotherowner@example.com",
            "password": "testpassword",
            "role": "bakery_owner"
        }
    )
    login = client.post(
        "/login",
        data={
            "username": "anotherowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    response = client.delete(
        f"/manage-menu?menu_item_id={bakery_and_menu['menu_item_id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not your bakery"

def test_delete_non_existing_menu_item(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    response = client.delete(
        "/manage-menu?menu_item_id=999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_owner_cannot_get_menu_items_of_other_owner(client, bakery_and_menu):
    register_another_owner = client.post(
        "/register",
        json={
            "username": "anotherowner",
            "email": "anotherowner@example.com",
            "password": "testpassword",
            "role": "bakery_owner"
        }
    )
    login = client.post(
        "/login",
        data={
            "username": "anotherowner@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    response = client.get(
        f"/bakeries/{bakery_and_menu['bakery_id']}/manage-menu",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not your bakery"
