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


def test_customer_creates_order_successfully(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )

    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert login.status_code == 200
    assert order.status_code == 200


def test_owner_cannot_create_order(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )

    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert login.status_code == 200
    assert order.status_code == 403

def test_create_order_with_invalid_bakery_id(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )

    order = client.post(
        "/orders",
        json={
            "bakery_id": 999,
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert login.status_code == 200
    assert order.status_code == 404

def test_create_order_with_invalid_menu_item_id(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )

    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": 999,
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert login.status_code == 200
    assert order.status_code == 404

def test_create_order_with_menu_item_from_different_bakery(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    response = client.post(
        "/bakery",
        json={
            "name": "Another Bakery",
            "description": "Another test bakery",
            "location": "Another Location"
        },
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    another_menu_item = client.post(
        "/manage-menu",
        json={
            "bakery_id": response.json()["id"],
            "name": "Another Test Bread",
            "description": "Another test bread",
            "price": 4.0
        },
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    logout = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    login_customer = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )

    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": another_menu_item.json()["id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {login_customer.json()['access_token']}"}
    )

    assert login_customer.status_code == 200
    assert order.status_code == 404

def test_create_order_with_invalid_quantity(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )

    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": -1
        },
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert login.status_code == 200
    assert order.status_code == 400

def test_customer_gets_own_orders(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    orders_response = client.get(
        "/my-orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert login.status_code == 200
    assert order.status_code == 200
    assert orders_response.status_code == 200
    assert orders_response.json()[0]["menu_item"] == "Test Bread"
    assert len(orders_response.json()) == 1

def test_customer_only_sees_own_orders(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    logout = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    register_another_customer = client.post(
        "/register",
        json={
            "username": "anothercustomer",
            "email": "anothercustomer@example.com",
            "password": "testpassword",
            "role": "customer"
        }
    )

    login_another_customer = client.post(
        "/login",
        data={
            "username": "anothercustomer@example.com",
            "password": "testpassword"
        }
    )
    
    another_token = login_another_customer.json()["access_token"]
    orders_response = client.get(
        "/my-orders",
        headers={"Authorization": f"Bearer {another_token}"}
    )
    assert login.status_code == 200
    assert order.status_code == 200
    assert login_another_customer.status_code == 200
    assert orders_response.status_code == 200
    assert len(orders_response.json()) == 0

def test_owner_cannot_access_my_orders(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    print("this is from test_owner_cannot_access_my_orders:", login.json())
    response = client.get(
        "/my-orders",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert login.status_code == 200
    assert response.status_code == 403

def test_owner_gets_incoming_orders_for_own_bakery(client, bakery_and_menu):
    login_customer = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token_customer = login_customer.json()["access_token"]
    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token_customer}"}
    )

    logout_customer = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {token_customer}"}
    )

    login_owner = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token_owner = login_owner.json()["access_token"]
    incoming_orders_response = client.get(
        "/incoming-orders",
        headers={"Authorization": f"Bearer {token_owner}"}
    )

    assert login_customer.status_code == 200
    assert login_owner.status_code == 200
    assert incoming_orders_response.status_code == 200
    assert incoming_orders_response.json()[0]["menu_item"] == "Test Bread"
    assert len(incoming_orders_response.json()) == 1

def test_owner_only_sees_orders_for_own_bakery(client, bakery_and_menu):
    login_customer = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token_customer = login_customer.json()["access_token"]
    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token_customer}"}
    )
    logout_customer = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {token_customer}"}
    )
    register_another_owner = client.post(
        "/register",
        json={
            "username": "anotherowner",
            "email": "anotherowner@example.com",
            "password": "testpassword",
            "role": "bakery_owner"
        }
    )
    login_another_owner = client.post(
        "/login",
        data={
            "username": "anotherowner@example.com",
            "password": "testpassword"
        }
    )
    another_token = login_another_owner.json()["access_token"]
    incoming_orders_response = client.get(
        "/incoming-orders",
        headers={"Authorization": f"Bearer {another_token}"}
    )
    assert login_customer.status_code == 200
    assert login_another_owner.status_code == 200
    assert incoming_orders_response.status_code == 200
    assert len(incoming_orders_response.json()) == 0

def test_customer_cannot_access_incoming_orders(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token = login.json()["access_token"]
    incoming_orders_response = client.get(
        "/incoming-orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert login.status_code == 200
    assert incoming_orders_response.status_code == 403

def test_owner_updates_order_status(client, bakery_and_menu):
    login_customer = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token_customer = login_customer.json()["access_token"]
    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token_customer}"}
    )
    logout_customer = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {token_customer}"}
    )
    login_owner = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token_owner = login_owner.json()["access_token"]
    update_status_response = client.patch(
        f"/orders/{order.json()['id']}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    print("this is from test_owner_updates_order_status:", update_status_response.json())
    assert login_customer.status_code == 200
    assert login_owner.status_code == 200
    assert update_status_response.status_code == 200
    assert update_status_response.json()["status"] == "completed"

def test_owner_cannot_update_other_owner_order(client, bakery_and_menu):
    login_customer = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token_customer = login_customer.json()["access_token"]
    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token_customer}"}
    )
    logout_customer = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {token_customer}"}
    )
    register_another_owner = client.post(
        "/register",
        json={
            "username": "anotherowner",
            "email": "anotherowner@example.com",
            "password": "testpassword",
            "role": "bakery_owner"
        }
    )
    login_another_owner = client.post(
        "/login",
        data={
            "username": "anotherowner@example.com",
            "password": "testpassword"
        }
    )
    another_token = login_another_owner.json()["access_token"]

    update_status_response = client.patch(
        f"/orders/{order.json()['id']}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {another_token}"}
    )
    assert login_customer.status_code == 200
    assert login_another_owner.status_code == 200
    assert update_status_response.status_code == 403
    assert update_status_response.json()["detail"] == "Not your order"

def test_customer_cannot_update_order_status(client, bakery_and_menu):
    login_customer = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token_customer = login_customer.json()["access_token"]

    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token_customer}"}
    )

    update_status_response = client.patch(
        f"/orders/{order.json()['id']}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {token_customer}"}
    )
    assert login_customer.status_code == 200
    assert update_status_response.status_code == 403

def test_update_non_existing_order_status(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token_owner = login.json()["access_token"]

    update_status_response = client.patch(
        "/orders/999/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    assert login.status_code == 200
    assert update_status_response.status_code == 404

def test_update_order_status_with_invalid_status(client, bakery_and_menu):
    login = client.post(
        "/login",
        data={
            "username": "testcustomer@example.com",
            "password": "testpassword"
        }
    )
    token_customer = login.json()["access_token"]

    order = client.post(
        "/orders",
        json={
            "bakery_id": bakery_and_menu["bakery_id"],
            "menu_item_id": bakery_and_menu["menu_item_id"],
            "quantity": 2
        },
        headers={"Authorization": f"Bearer {token_customer}"}
    )

    logout = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {token_customer}"}
    )

    login_owner = client.post(
        "/login",
        data={
            "username": "testowner@example.com",
            "password": "testpassword"
        }
    )
    token_owner = login_owner.json()["access_token"]

    update_status_response = client.patch(
        f"/orders/{order.json()['id']}/status",
        json={"status": "eating your bread currently"},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    print("this is from test_update_order_status_with_invalid_status:", update_status_response.json())
    assert login.status_code == 200
    assert update_status_response.status_code == 422