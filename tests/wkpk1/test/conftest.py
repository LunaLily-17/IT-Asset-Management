
import copy

import pytest
from fastapi.testclient import TestClient

from main import app
from database import db_json


@pytest.fixture
def client(tmp_path, monkeypatch):
    original_data = copy.deepcopy(db_json.DB)

    monkeypatch.setattr(
        db_json,
        "DB_FILE_PATH",
        tmp_path / "test_itam_db.json"
    )

    db_json.DB.clear()
    db_json.DB.update({
        "assets": {},
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
        "category": "Hardware",
        "asset_type": "Laptop",
        "manufacturer": "Dell",
        "product": "Latitude 5450",
        "serial_number": "SN-001",
        "location": "Leicester Office",
        "status": "Available"
    }


@pytest.fixture
def software_asset():
    return {
        "title": "Visual Studio Code",
        "category": "Software",
        "asset_type": "Application",
        "product": "Visual Studio Code",
        "manufacturer": "Microsoft",
        "version": "1.0",
        "unique_identifier": "INSTALL-001",
        "location": "Development Workstation",
        "status": "Available"
    }


@pytest.fixture
def virtual_asset():
    return {
        "title": "Development VM",
        "category": "Hardware",
        "asset_type": "Virtual Machine",
        "unique_identifier": "VM-001",
        "location": "Private Cloud",
        "status": "Available"
    }
