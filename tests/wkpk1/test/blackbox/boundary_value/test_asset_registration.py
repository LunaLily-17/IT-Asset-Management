import pytest
from database import db_json


# TC20 - Purchase Cost Boundary Value Analysis
# Purpose: Verify validation at and around the minimum cost.
# Technique: Black-box / Boundary Value Analysis
# Boundary: Cost must be >= 0.
# Test values:
#   -0.01 -> Invalid (just below boundary)
#    0.00 -> Valid   (at boundary)
#    0.01 -> Valid   (just above boundary)
# Expected: HTTP 422 for invalid, HTTP 201 for valid.

@pytest.mark.parametrize(
    "cost, expected_status",
    [
        (-0.01, 422),
        (0.00, 201),
        (0.01, 201)
    ]
)
def test_purchase_cost_boundary(
    client, physical_asset, cost, expected_status
):
    physical_asset["cost"] = cost

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == expected_status

    if expected_status == 422:
        assert db_json.DB["hardware_assets"] == {}
    else:
        assert len(db_json.DB["hardware_assets"]) == 1


# TC23 - Asset Title Length Boundary Value Analysis
# Purpose: Verify the minimum valid asset title length.
# Technique: Black-box / Boundary Value Analysis
# Boundary: Title must contain at least one non-space character.
# Test values:
#   ""    -> Invalid (length 0)
#   "A"   -> Valid   (length 1)
#   "AB"  -> Valid   (length 2)
#   "   " -> Invalid (whitespace-only)
# Expected: HTTP 422 for invalid, HTTP 201 for valid.

@pytest.mark.parametrize(
    "title, expected_status",
    [
        ("", 422),
        ("A", 201),
        ("AB", 201),
        ("   ", 422)
    ]
)
def test_asset_title_boundary(
    client, physical_asset, title, expected_status
):
    physical_asset["title"] = title

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == expected_status

    if expected_status == 422:
        assert db_json.DB["hardware_assets"] == {}
    else:
        assert len(db_json.DB["hardware_assets"]) == 1
