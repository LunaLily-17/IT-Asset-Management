"""Per-test JSON isolation: never touch the real ITAM database."""
import copy

import pytest
from fastapi.testclient import TestClient

from database import db_json
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    original = copy.deepcopy(db_json.DB)
    monkeypatch.setattr(db_json, "DB_FILE_PATH", tmp_path / "test_itam_db.json")
    with db_json.DB_LOCK:
        db_json.DB.clear()
        db_json.DB.update({name: {} for name in db_json.COLLECTIONS})
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        with db_json.DB_LOCK:
            db_json.DB.clear()
            db_json.DB.update(original)


@pytest.fixture
def hardware():
    return {
        "title": "Dell Latitude 5450", "category": "Hardware", "asset_type": "Laptop",
        "manufacturer": "Dell", "model": "Latitude 5450",
        "serial_number": "SN-001", "location": "IT Office", "status": "Available",
    }


@pytest.fixture
def software():
    return {
        "title": "VS Code", "category": "Software", "asset_type": "Application",
        "vendor": "Microsoft", "product": "Visual Studio Code", "version": "1.0",
        "installation_id": "INSTALL-001", "location": "Development PC", "status": "Available",
    }


@pytest.fixture
def virtual_machine():
    return {
        "title": "Development VM", "category": "Hardware", "asset_type": "Virtual Machine",
        "unique_identifier": "VM-001", "location": "Private Cloud", "status": "Available",
    }
