
import copy

import pytest
from fastapi.testclient import TestClient

from main import app
from database import db_json


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Isolate each test using a temporary JSON database."""
    original_data = copy.deepcopy(db_json.DB)

    test_file = tmp_path / "test_itam_db.json"
    monkeypatch.setattr(db_json, "DB_FILE_PATH", test_file)

    db_json.DB.clear()
    db_json.DB.update({
        "hardware_assets": {},
        "software_licences": {},
        "asset_retirements": {}
    })

    db_json.save_db()

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        db_json.DB.clear()
        db_json.DB.update(original_data)


@pytest.fixture
def physical_asset():
    return {
        "title": "Dell Latitude 5450",
        "product": "Latitude 5450",
        "category": "Physical",
        "asset_type": "Laptop",
        "manufacturer": "Dell",
        "serial_number": "SN-001",
        "location": "Leicester Office",
        "status": "Available"
    }


@pytest.fixture
def virtual_asset():
    return {
        "title": "Development VM",
        "category": "Virtual",
        "asset_type": "Virtual Machine",
        "unique_identifier": "VM-001",
        "location": "Private Cloud",
        "status": "Available"
    }
