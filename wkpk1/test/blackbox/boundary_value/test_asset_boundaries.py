"""BV01–BV09: boundaries on strings, dates, costs and optional details."""
import pytest
from database import db_json


@pytest.mark.parametrize("title", ["", " ", "x" * 151])
def test_bv01_reject_invalid_title(client, hardware, title):
    hardware["title"] = title
    assert client.post("/assets", json=hardware).status_code == 422


def test_bv02_accept_title_at_max_length(client, hardware):
    hardware["title"] = "x" * 150
    assert client.post("/assets", json=hardware).status_code == 201


def test_bv03_trim_title(client, hardware):
    hardware["title"] = "  New laptop  "
    response = client.post("/assets", json=hardware)
    assert response.status_code == 201
    assert response.json()["title"] == "New laptop"


@pytest.mark.parametrize("cost,valid", [(0, True), (0.01, True), (-0.01, False), ("abc", False), ("NaN", False), ("Infinity", False)])
def test_bv04_cost_boundaries(client, software, cost, valid):
    software["cost"] = cost
    response = client.post("/assets", json=software)
    assert response.status_code == (201 if valid else 422)


def test_bv05_optional_dates_persist(client, hardware):
    hardware.update(purchase_date="2026-10-01", warranty_expiry="2028-10-01", supplier="IT Supplier", cost=1000.50)
    response = client.post("/assets", json=hardware)
    assert response.status_code == 201
    assert response.json()["purchase_date"] == "2026-10-01"
    assert response.json()["warranty_expiry"] == "2028-10-01"
    assert response.json()["cost"] == 1000.50


def test_bv06_invalid_date(client, hardware):
    hardware["purchase_date"] = "not-a-date"
    assert client.post("/assets", json=hardware).status_code == 422


@pytest.mark.parametrize("field", ["title", "location", "manufacturer", "model", "serial_number"])
def test_bv07_blank_hardware_values(client, hardware, field):
    hardware[field] = "  "
    assert client.post("/assets", json=hardware).status_code == 422


@pytest.mark.parametrize("field", ["vendor", "product", "version", "installation_id"])
def test_bv08_blank_software_values(client, software, field):
    software[field] = " "
    assert client.post("/assets", json=software).status_code == 422


def test_bv09_invalid_request_no_side_effect(client, hardware):
    hardware["cost"] = -1
    assert client.post("/assets", json=hardware).status_code == 422
    assert not db_json.DB["hardware_assets"]
