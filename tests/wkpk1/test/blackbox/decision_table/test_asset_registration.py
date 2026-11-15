
from database import db_json


# TC10 - Duplicate Hardware Serial
# Purpose: Reject repeated hardware serial numbers.
# Technique: Black-box / Decision Table
# Expected: First 201, second 409.
def test_duplicate_hardware(client, physical_asset):
    first = client.post("/assets", json=physical_asset)
    second = client.post("/assets", json=physical_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["assets"]) == 1


# TC11 - Duplicate Software Installation Identifier
# Purpose: Reject repeated software installation identifiers.
# Technique: Black-box / Decision Table
# Expected: First 201, second 409.
def test_duplicate_software(client, software_asset):
    first = client.post("/assets", json=software_asset)
    second = client.post("/assets", json=software_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["assets"]) == 1


# TC12 - Duplicate Identifier Across Categories
# Purpose: Prevent an identifier being reused across categories.
# Technique: Black-box / Decision Table
# Expected: Second registration rejected with HTTP 409.
def test_cross_category_duplicate(
    client, physical_asset, software_asset
):
    physical_asset["serial_number"] = "SHARED-001"
    software_asset["unique_identifier"] = "SHARED-001"

    first = client.post("/assets", json=physical_asset)
    second = client.post("/assets", json=software_asset)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(db_json.DB["assets"]) == 1
