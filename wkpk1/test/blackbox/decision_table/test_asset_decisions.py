"""DT01–DT07: registration decision rules including duplicate scenarios."""
from database import db_json


def test_dt01_duplicate_hardware_serial(client, hardware):
    assert client.post("/assets", json=hardware).status_code == 201
    assert client.post("/assets", json=hardware).status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1


def test_dt02_duplicate_hardware_case_insensitive(client, hardware):
    assert client.post("/assets", json=hardware).status_code == 201
    hardware["serial_number"] = "sn-001"
    assert client.post("/assets", json=hardware).status_code == 409


def test_dt03_duplicate_hardware_across_identifier_fields(client, hardware):
    assert client.post("/assets", json=hardware).status_code == 201
    hardware.pop("serial_number")
    hardware["unique_identifier"] = "sn-001"
    assert client.post("/assets", json=hardware).status_code == 409


def test_dt04_duplicate_software_installation(client, software):
    assert client.post("/assets", json=software).status_code == 201
    software["installation_id"] = "install-001"
    assert client.post("/assets", json=software).status_code == 409
    assert len(db_json.DB["software_assets"]) == 1


def test_dt05_same_software_product_different_installations(client, software):
    assert client.post("/assets", json=software).status_code == 201
    software["installation_id"] = "INSTALL-002"
    assert client.post("/assets", json=software).status_code == 201
    assert len(db_json.DB["software_assets"]) == 2


def test_dt06_same_identifier_text_in_different_namespaces(client, hardware, software):
    hardware["serial_number"] = "COMMON-ID"
    software["installation_id"] = "COMMON-ID"
    assert client.post("/assets", json=hardware).status_code == 201
    assert client.post("/assets", json=software).status_code == 201


def test_dt07_two_different_assets_receive_unique_ids(client, hardware):
    first = client.post("/assets", json=hardware)
    hardware["serial_number"] = "SN-002"
    second = client.post("/assets", json=hardware)
    assert first.status_code == second.status_code == 201
    assert first.json()["asset_id"] != second.json()["asset_id"]
