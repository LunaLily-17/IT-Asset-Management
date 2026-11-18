"""
Pytest tests for the System Administrator API.

Assumed routes:
  POST   /api/v1/admin/users
  GET    /api/v1/admin/users/{user_id}
  PUT    /api/v1/admin/users/{user_id}
  PATCH  /api/v1/admin/users/{user_id}/deactivate
  GET    /api/v1/admin/roles
  GET    /api/v1/admin/roles/{role_name}/permissions
  POST   /api/v1/admin/users/{user_id}/role
  GET    /api/v1/admin/asset-categories
  POST   /api/v1/admin/asset-categories
  PUT    /api/v1/admin/asset-categories/{category_id}
  GET    /api/v1/admin/asset-statuses

Run from the project root:
    python -m pip install pytest httpx
    python -m pytest -v

Assumes main.py exports `app`. Adjust route paths and JSON fields if your
implementation uses different names. These tests do not test authentication.
"""

import uuid

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
BASE_URL = "/api/v1/admin"


def unique_email():
    return f"test-{uuid.uuid4().hex[:10]}@example.com"


def create_user_payload(**overrides):
    payload = {
        "name": "Pytest System Admin User",
        "email": unique_email(),
        "role": "Employee",
    }
    payload.update(overrides)
    return payload


def create_user():
    response = client.post(
        f"{BASE_URL}/users",
        json=create_user_payload(),
    )
    assert response.status_code in (200, 201), response.text
    return response.json()


# SA Task 1: User account management

def test_create_user_with_valid_details():
    response = client.post(
        f"{BASE_URL}/users",
        json=create_user_payload(),
    )
    assert response.status_code in (200, 201)
    assert response.json().get("id") is not None


def test_create_user_rejects_missing_required_field():
    payload = create_user_payload()
    payload.pop("name")
    response = client.post(f"{BASE_URL}/users", json=payload)
    assert response.status_code == 422


def test_create_user_rejects_invalid_email():
    response = client.post(
        f"{BASE_URL}/users",
        json=create_user_payload(email="not-an-email"),
    )
    assert response.status_code == 422


def test_get_existing_user():
    user = create_user()
    response = client.get(f"{BASE_URL}/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


def test_get_nonexistent_user_returns_404():
    response = client.get(f"{BASE_URL}/users/99999999")
    assert response.status_code == 404


def test_update_existing_user():
    user = create_user()
    response = client.put(
        f"{BASE_URL}/users/{user['id']}",
        json={"name": "Updated Pytest User"},
    )
    assert response.status_code == 200
    assert response.json().get("name") == "Updated Pytest User"


def test_deactivate_existing_user():
    user = create_user()
    response = client.patch(
        f"{BASE_URL}/users/{user['id']}/deactivate"
    )
    assert response.status_code == 200
    assert str(response.json().get("status", "")).lower() in (
        "inactive", "deactivated"
    )


# SA Task 2: Role and permission management

def test_get_roles():
    response = client.get(f"{BASE_URL}/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_permissions_for_existing_role():
    # "Employee" is assumed to be seeded in the in-memory role data.
    response = client.get(f"{BASE_URL}/roles/Employee/permissions")
    assert response.status_code == 200
    assert isinstance(response.json(), (dict, list))


def test_get_permissions_for_unknown_role_returns_404():
    response = client.get(
        f"{BASE_URL}/roles/role-that-does-not-exist/permissions"
    )
    assert response.status_code == 404


def test_assign_valid_role_to_user():
    user = create_user()
    response = client.post(
        f"{BASE_URL}/users/{user['id']}/role",
        json={"role": "Asset Manager"},
    )
    assert response.status_code == 200


def test_assign_invalid_role_is_rejected():
    user = create_user()
    response = client.post(
        f"{BASE_URL}/users/{user['id']}/role",
        json={"role": "NotARealRole"},
    )
    assert response.status_code in (400, 404, 422)


# SA Task 3: Asset categories and reference values

def test_get_asset_categories():
    response = client.get(f"{BASE_URL}/asset-categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_asset_category():
    category_name = f"Pytest Category {uuid.uuid4().hex[:8]}"
    response = client.post(
        f"{BASE_URL}/asset-categories",
        json={"name": category_name},
    )
    assert response.status_code in (200, 201), response.text
    assert response.json().get("name") == category_name


def test_create_asset_category_rejects_missing_name():
    response = client.post(
        f"{BASE_URL}/asset-categories",
        json={},
    )
    assert response.status_code == 422


def test_update_asset_category():
    category_name = f"Pytest Category {uuid.uuid4().hex[:8]}"
    created = client.post(
        f"{BASE_URL}/asset-categories",
        json={"name": category_name},
    )
    assert created.status_code in (200, 201), created.text
    category_id = created.json()["id"]

    updated_name = f"Updated {category_name}"
    response = client.put(
        f"{BASE_URL}/asset-categories/{category_id}",
        json={"name": updated_name},
    )
    assert response.status_code == 200
    assert response.json().get("name") == updated_name


def test_update_nonexistent_asset_category_returns_404():
    response = client.put(
        f"{BASE_URL}/asset-categories/99999999",
        json={"name": "Does Not Exist"},
    )
    assert response.status_code == 404


def test_get_asset_status_reference_values():
    response = client.get(f"{BASE_URL}/asset-statuses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_api_unknown_route_returns_404():
    response = client.get(f"{BASE_URL}/route-that-does-not-exist")
    assert response.status_code == 404
