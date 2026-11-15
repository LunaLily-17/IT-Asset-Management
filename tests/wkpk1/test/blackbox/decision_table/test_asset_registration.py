import pytest
from database import db_json

# TC11 - Duplicate Physical Serial Number
# Purpose: Prevent two physical assets from using the same serial.
# Covers: Duplicate identifier business rule and AC3.
# Expected: First request 201, second 409, inventory unchanged.
def test_duplicate_serial(client, physical_asset):
    first = client.post("/assets", json=physical_asset)
    second = client.post("/assets", json=physical_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1


# TC12 - Duplicate Virtual Identifier
# Purpose: Prevent duplicate virtual machine identifiers.
# Covers: Identifier uniqueness business rule and AC3.
# Expected: First request 201, second 409, only one record.
def test_duplicate_virtual_identifier(client, virtual_asset):
    first = client.post("/assets", json=virtual_asset)
    second = client.post("/assets", json=virtual_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1


# TC21 - Case-Insensitive Duplicate Identifier
# Purpose: Ensure serial numbers differing only in case
# cannot bypass duplicate detection.
# Covers: Identifier normalisation and AC3.
# Expected: HTTP 409 on second registration.
def test_case_insensitive_duplicate(client, physical_asset):
    first = client.post("/assets", json=physical_asset)

    physical_asset["serial_number"] = "sn-001"
    second = client.post("/assets", json=physical_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1

# TC24 - Cross-Category Duplicate Identifier
# Purpose: Prevent a physical serial number from being reused
# as a virtual asset identifier.
# Covers: Cross-category uniqueness and AC3.
# Expected: Second registration returns HTTP 409.
def test_cross_category_duplicate(
    client, physical_asset, virtual_asset
):
    physical_asset["serial_number"] = "SHARED-001"
    virtual_asset["unique_identifier"] = "SHARED-001"

    first = client.post("/assets", json=physical_asset)
    second = client.post("/assets", json=virtual_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["hardware_assets"]) == 1
