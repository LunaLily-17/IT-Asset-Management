import pytest
from database import db_json
import json

# TC18 - Unique Internal Asset ID Generation
# Purpose: Verify separate registrations generate different IDs.
# Covers: Unique internal asset ID business rule and AC1.
# Expected: Both 201, two different hardware IDs.
def test_unique_generated_ids(client, physical_asset):
    first = client.post("/assets", json=physical_asset)

    physical_asset["serial_number"] = "SN-002"
    second = client.post("/assets", json=physical_asset)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["hardware_id"] != second.json()["hardware_id"]
    assert len(db_json.DB["hardware_assets"]) == 2


# TC19 - Retrieve Registered Asset
# Purpose: Verify that a newly registered asset is retrievable.
# Covers: AC4 - Retrieval API integration.
# Expected: HTTP 200 and correct asset details.
def test_retrieve_registered_asset(client, physical_asset):
    created = client.post("/assets", json=physical_asset)

    assert created.status_code == 201
    hardware_id = created.json()["hardware_id"]

    response = client.get(f"/assets/{hardware_id}")

    assert response.status_code == 200
    assert response.json()["hardware_id"] == hardware_id
    assert response.json()["serial_number"] == "SN-001"


# TC20 - JSON Persistence and Reload
# Purpose: Verify successful registrations survive database reload.
# Covers: In-memory inventory integration and AC4.
# Expected: Saved JSON contains the asset and GET returns it
# after reloading the database.
def test_json_persistence(client, physical_asset):
    created = client.post("/assets", json=physical_asset)

    assert created.status_code == 201
    hardware_id = created.json()["hardware_id"]

    with open(db_json.DB_FILE_PATH, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert hardware_id in saved_data["hardware_assets"]

    db_json.DB.clear()
    db_json.load_db()

    response = client.get(f"/assets/{hardware_id}")

    assert response.status_code == 200
    assert response.json()["hardware_id"] == hardware_id


# TC21 - Optional Purchase Details Preserved
# Purpose: Verify optional purchase information is correctly
# stored and returned through the retrieval API.
# Covers: Data integrity and AC4.
# Expected: HTTP 201, then GET 200 with matching details.
def test_purchase_details_preserved(client, physical_asset):
    physical_asset.update({
        "purchase_date": "2026-11-01",
        "supplier": "Dell UK",
        "cost": 950.00,
        "warranty_expiry": "2029-11-01"
    })

    created = client.post("/assets", json=physical_asset)

    assert created.status_code == 201

    hardware_id = created.json()["hardware_id"]
    response = client.get(f"/assets/{hardware_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["purchase_date"] == "2026-11-01"
    assert data["supplier"] == "Dell UK"
    assert data["cost"] == 950.00
    assert data["warranty_expiry"] == "2029-11-01"
