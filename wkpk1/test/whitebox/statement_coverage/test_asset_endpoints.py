"""ST01–ST09: successful service paths and persistence read/write behaviour."""
import json
from database import db_json


def test_st01_get_hardware_by_id(client, hardware):
    created = client.post("/assets", json=hardware).json()
    fetched = client.get(f"/assets/{created['asset_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["asset_id"] == created["asset_id"]
    assert fetched.json()["category"] == created["category"]
    assert "assigned_employee_id" not in fetched.json()


def test_st02_get_software_by_id(client, software):
    created = client.post("/assets", json=software).json()
    fetched = client.get(f"/assets/{created['asset_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["asset_id"] == created["asset_id"]
    assert fetched.json()["category"] == created["category"]
    assert "assigned_employee_id" not in fetched.json()


def test_st03_list_both_categories(client, hardware, software):
    client.post("/assets", json=hardware)
    client.post("/assets", json=software)
    response = client.get("/assets")
    assert response.status_code == 200
    assert {item["category"] for item in response.json()} == {"Hardware", "Software"}


def test_st04_filter_hardware(client, hardware, software):
    client.post("/assets", json=hardware)
    client.post("/assets", json=software)
    items = client.get("/assets?category=Hardware").json()
    assert len(items) == 1 and items[0]["category"] == "Hardware"


def test_st05_filter_software(client, hardware, software):
    client.post("/assets", json=hardware)
    client.post("/assets", json=software)
    items = client.get("/assets?category=Software").json()
    assert len(items) == 1 and items[0]["category"] == "Software"


def test_st06_invalid_filter(client):
    assert client.get("/assets?category=Other").status_code == 422


def test_st07_reload_persisted_db(client, hardware, software):
    client.post("/assets", json=hardware)
    client.post("/assets", json=software)
    db_json.DB["hardware_assets"].clear()
    db_json.DB["software_assets"].clear()
    db_json.load_db()
    assert len(db_json.DB["hardware_assets"]) == 1
    assert len(db_json.DB["software_assets"]) == 1


def test_st08_preserve_unrelated_collections(client, hardware):
    db_json.DB["software_licences"]["LIC-001"] = {"key": "existing"}
    db_json.save_db()
    client.post("/assets", json=hardware)
    assert db_json.DB["software_licences"]["LIC-001"] == {"key": "existing"}
    with db_json.DB_FILE_PATH.open(encoding="utf-8") as handle:
        persisted = json.load(handle)
    assert persisted["software_licences"]["LIC-001"] == {"key": "existing"}


def test_st09_timestamps_set(client, software):
    record = client.post("/assets", json=software).json()
    assert record["created_at"]
    assert record["updated_at"]
