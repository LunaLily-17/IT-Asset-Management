
import pytest
from database import db_json


# TC01 - Valid Hardware Registration
# Purpose: Verify hardware assets are accepted.
# Technique: Black-box / Category Partition
# Expected: HTTP 201 and server-generated asset ID.
def test_valid_hardware(client, physical_asset):
    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 201
    assert response.json()["category"] == "Hardware"
    assert response.json()["asset_id"].startswith("AST-")


# TC02 - Valid Software Registration
# Purpose: Verify software assets can be registered.
# Technique: Black-box / Category Partition
# Expected: HTTP 201, correct category and product.
def test_valid_software(client, software_asset):
    response = client.post("/assets", json=software_asset)

    assert response.status_code == 201
    assert response.json()["category"] == "Software"
    assert response.json()["product"] == "Visual Studio Code"


# TC03 - Valid Virtual Infrastructure Registration
# Purpose: Verify virtual infrastructure is supported.
# Technique: Black-box / Category Partition
# Expected: HTTP 201 without physical serial number.
def test_valid_virtual_machine(client, virtual_asset):
    response = client.post("/assets", json=virtual_asset)

    assert response.status_code == 201
    assert response.json()["asset_type"] == "Virtual Machine"


# TC04 - Missing Common Mandatory Fields
# Purpose: Reject missing title, category, type, location or status.
# Technique: Black-box / Category Partition
# Expected: HTTP 422 and unchanged inventory.
@pytest.mark.parametrize(
    "field",
    ["title", "category", "asset_type", "location", "status"]
)
def test_missing_common_field(client, physical_asset, field):
    physical_asset.pop(field)

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["assets"] == {}


# TC05 - Missing Hardware-Specific Fields
# Purpose: Verify conditional hardware validation.
# Technique: Black-box / Category Partition
# Expected: HTTP 422 for missing manufacturer or model.
@pytest.mark.parametrize(
    "field",
    ["manufacturer", "product"]
)
def test_missing_hardware_field(client, physical_asset, field):
    physical_asset.pop(field)

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["assets"] == {}


# TC06 - Missing Hardware Identifier
# Purpose: Require a serial number or alternate identifier.
# Technique: Black-box / Category Partition
# Expected: HTTP 422.
def test_missing_hardware_identifier(client, physical_asset):
    physical_asset.pop("serial_number")

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422


# TC07 - Missing Software Product
# Purpose: Verify conditional software validation.
# Technique: Black-box / Category Partition
# Expected: HTTP 422.
def test_missing_software_product(client, software_asset):
    software_asset.pop("product")

    response = client.post("/assets", json=software_asset)

    assert response.status_code == 422


# TC08 - Invalid Hardware/Software Type Combination
# Purpose: Reject software types under hardware category.
# Technique: Black-box / Category Partition
# Expected: HTTP 422.
def test_invalid_category_type(client, physical_asset):
    physical_asset["asset_type"] = "Application"

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422


# TC09 - Prevent Employee Assignment
# Purpose: Ensure registration cannot silently assign assets.
# Technique: Black-box / Category Partition
# Expected: HTTP 422 for client-supplied assignment.
def test_forbidden_assignment(client, physical_asset):
    physical_asset["assigned_employee_id"] = "EMP-001"

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
