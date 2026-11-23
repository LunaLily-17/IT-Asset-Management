
from copy import deepcopy
from unittest.mock import patch

import pytest

from database import db_json
from models.asset_request import AssetAssignmentRequest
from services import asset_service


@pytest.fixture
def service_data(tmp_path, monkeypatch):
    original_db = deepcopy(db_json.DB)

    monkeypatch.setattr(
        db_json,
        "DB_FILE_PATH",
        tmp_path / "service_test_db.json",
    )

    db_json.DB.clear()
    db_json.DB.update({
        "hardware_assets": {
            "HW-001": {
                "asset_id": "HW-001",
                "category": "Hardware",
                "title": "Test Laptop",
                "status": "Available",
                "assigned_employee_id": None,
            }
        },
        "software_assets": {},
        "employees": {
            "EMP-001": {
                "employee_id": "EMP-001",
                "status": "Active",
            }
        },
        "asset_assignments": {},
        "audit_logs": {},
    })

    try:
        yield
    finally:
        db_json.DB.clear()
        db_json.DB.update(original_db)


def test_successful_assignment_service(service_data):
    request = AssetAssignmentRequest(
        employee_id="EMP-001"
    )

    result = asset_service.assign_asset(
        "HW-001", request, "MANAGER-001"
    )

    assert result["status"] == "Active"
    assert result["assigned_by"] == "MANAGER-001"


def test_save_failure_rolls_back(service_data):
    request = AssetAssignmentRequest(
        employee_id="EMP-001"
    )

    original_asset = deepcopy(
        db_json.DB["hardware_assets"]["HW-001"]
    )

    with patch.object(
        db_json,
        "save_db",
        side_effect=OSError("Simulated save failure"),
    ):
        with pytest.raises(OSError):
            asset_service.assign_asset(
                "HW-001", request, "MANAGER-001"
            )

    assert (
        db_json.DB["hardware_assets"]["HW-001"]
        == original_asset
    )
    assert db_json.DB["asset_assignments"] == {}
    assert db_json.DB["audit_logs"] == {}


def test_missing_actor_rejected(service_data):
    request = AssetAssignmentRequest(
        employee_id="EMP-001"
    )

    with pytest.raises(PermissionError):
        asset_service.assign_asset(
            "HW-001", request, ""
        )


def test_active_assignment_conflict(service_data):
    request = AssetAssignmentRequest(
        employee_id="EMP-001"
    )

    asset_service.assign_asset(
        "HW-001", request, "MANAGER-001"
    )

    with pytest.raises(
        asset_service.AssetAssignmentConflict
    ):
        asset_service.assign_asset(
            "HW-001", request, "MANAGER-001"
        )
