"""CP01–CP16: valid/invalid equivalence classes for registration."""
import pytest
from database import db_json


def test_cp01_register_physical_hardware(client, hardware):
    result = client.post("/assets", json=hardware)
    assert result.status_code == 201
    assert result.json()["asset_id"].startswith("HW-")
    assert result.json()["assigned_employee_id"] is None
    assert result.json()["serial_number"] == "SN-001"
    assert len(db_json.DB["hardware_assets"]) == 1


def test_cp02_register_software(client, software):
    result = client.post("/assets", json=software)
    assert result.status_code == 201
    assert result.json()["asset_id"].startswith("SW-")
    assert result.json()["version"] == "1.0"
    assert result.json()["assigned_employee_id"] is None
    assert len(db_json.DB["software_assets"]) == 1


def test_cp03_register_virtual_machine(client, virtual_machine):
    result = client.post("/assets", json=virtual_machine)
    assert result.status_code == 201
    assert result.json()["asset_type"] == "Virtual Machine"


@pytest.mark.parametrize("missing", ["title", "category", "asset_type", "location"])
def test_cp04_missing_shared_fields(client, hardware, missing):
    hardware.pop(missing)
    assert client.post("/assets", json=hardware).status_code == 422
    assert db_json.DB["hardware_assets"] == {}


@pytest.mark.parametrize("field", ["manufacturer", "model"])
def test_cp05_missing_physical_hw_fields(client, hardware, field):
    hardware.pop(field)
    assert client.post("/assets", json=hardware).status_code == 422


def test_cp06_missing_hardware_identifiers(client, hardware):
    hardware.pop("serial_number")
    assert client.post("/assets", json=hardware).status_code == 422


def test_cp07_hardware_alternate_identifier(client, hardware):
    hardware.pop("serial_number")
    hardware["unique_identifier"] = "ASSET-TAG-001"
    assert client.post("/assets", json=hardware).status_code == 201


@pytest.mark.parametrize("field", ["vendor", "product", "version", "installation_id"])
def test_cp08_missing_software_fields(client, software, field):
    software.pop(field)
    assert client.post("/assets", json=software).status_code == 422


@pytest.mark.parametrize("category,asset_type", [("Hardware", "Application"), ("Software", "Laptop")])
def test_cp09_wrong_category_type(client, hardware, software, category, asset_type):
    request = hardware if category == "Hardware" else software
    request["asset_type"] = asset_type
    assert client.post("/assets", json=request).status_code == 422


@pytest.mark.parametrize("category", ["Consumable", "Physical", "", None])
def test_cp10_invalid_category(client, hardware, category):
    hardware["category"] = category
    assert client.post("/assets", json=hardware).status_code == 422


def test_cp11_no_employee_assignment_allowed(client, hardware):
    hardware["assigned_employee_id"] = "EMP-101"
    assert client.post("/assets", json=hardware).status_code == 422


def test_cp12_no_licence_fields_in_software_registration(client, software):
    software["licence_key"] = "SECRET"
    assert client.post("/assets", json=software).status_code == 422


def test_cp13_software_fields_disallowed_in_hardware(client, hardware):
    hardware["vendor"] = "Microsoft"
    assert client.post("/assets", json=hardware).status_code == 422


def test_cp14_hardware_fields_disallowed_in_software(client, software):
    software["serial_number"] = "SN-123"
    assert client.post("/assets", json=software).status_code == 422


def test_cp15_invalid_status(client, software):
    software["status"] = "Assigned"
    assert client.post("/assets", json=software).status_code == 422


def test_cp16_status_defaults_to_available(client, software):
    software.pop("status")
    response = client.post("/assets", json=software)
    assert response.status_code == 201
    assert response.json()["status"] == "Available"
