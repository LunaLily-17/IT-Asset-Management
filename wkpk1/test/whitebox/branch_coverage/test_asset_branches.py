"""BR01–BR09: exception/not-found/rare branches and rollback paths."""
import json
from unittest.mock import patch

import pytest
from database import db_json
from models.asset_request import HardwareRegistrationRequest, SoftwareRegistrationRequest
from services import asset_service


def test_br01_hardware_save_failure_rolls_back(client, hardware, monkeypatch):
    request = HardwareRegistrationRequest(**hardware)
    monkeypatch.setattr(db_json, "save_db", lambda: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(OSError):
        asset_service.register_asset(request)
    assert db_json.DB["hardware_assets"] == {}


def test_br02_software_save_failure_rolls_back(client, software, monkeypatch):
    request = SoftwareRegistrationRequest(**software)
    monkeypatch.setattr(db_json, "save_db", lambda: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(OSError):
        asset_service.register_asset(request)
    assert db_json.DB["software_assets"] == {}


@pytest.mark.parametrize("asset_id", ["HW-NOTFOUND", "SW-NOTFOUND", "UNKNOWN"])
def test_br03_unknown_asset_returns_404(client, asset_id):
    assert client.get(f"/assets/{asset_id}").status_code == 404


def test_br04_reject_unsupported_service_type(client):
    with pytest.raises(TypeError):
        asset_service.register_asset(object())


def test_br05_generate_id_retries_collision(client):
    fake_uuid = type("FakeUUID", (), {"hex": "0123456789abcdef0123456789abcdef"})()
    collection = {"HW-0123456789AB": {}}
    with patch.object(asset_service, "uuid4", side_effect=[fake_uuid, type("FakeUUID", (), {"hex": "fedcba9876543210"})()]):
        value = asset_service._generate_asset_id("HW", collection)
    assert value == "HW-FEDCBA987654"


def test_br06_load_legacy_db_adds_missing_collections(client):
    db_json.DB_FILE_PATH.write_text(json.dumps({"hardware_assets": {}, "external_team_data": {"x": 1}}))
    db_json.load_db()
    assert db_json.DB["software_assets"] == {}
    assert db_json.DB["external_team_data"] == {"x": 1}


def test_br07_corrupt_database_root_is_rejected(client):
    db_json.DB_FILE_PATH.write_text("[]")
    with pytest.raises(ValueError, match="root"):
        db_json.load_db()


def test_br08_corrupt_collection_is_rejected(client):
    db_json.DB_FILE_PATH.write_text('{"hardware_assets": []}')
    with pytest.raises(ValueError, match="collection"):
        db_json.load_db()


def test_br09_db_write_failure_does_not_leave_temp_file(client, monkeypatch):
    def broken_replace(*args):
        raise OSError("replace failed")
    monkeypatch.setattr(db_json.os, "replace", broken_replace)
    with pytest.raises(OSError):
        db_json.save_db()
    assert not (db_json.DB_FILE_PATH.parent / "test_itam_db.json.tmp").exists()
