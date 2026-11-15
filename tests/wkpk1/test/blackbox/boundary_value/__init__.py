
# TC20 - Negative Purchase Cost
# Purpose: Reject invalid negative purchase costs.
# Covers: Boundary validation and data integrity.
# Expected: HTTP 422, no record created.
def test_negative_cost(client, physical_asset):
    physical_asset["cost"] = -100

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}

# TC23 - Whitespace-Only Mandatory Field
# Purpose: Prevent blank asset names from being accepted.
# Covers: Input validation and AC2.
# Expected: HTTP 422, no record created.
def test_whitespace_title(client, physical_asset):
    physical_asset["title"] = "   "

    response = client.post("/assets", json=physical_asset)

    assert response.status_code == 422
    assert db_json.DB["hardware_assets"] == {}

