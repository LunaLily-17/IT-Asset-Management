import pytest
from database import db_json

# TC22 - Retrieve Non-Existent Asset
# Purpose: Verify correct error handling for unknown IDs.
# Covers: Negative retrieval API testing.
# Expected: HTTP 404.
def test_unknown_asset(client):
    response = client.get("/assets/HW-UNKNOWN")

    assert response.status_code == 404


from unittest.mock import patch
# TC25 - Database Save Failure
# Purpose: Verify that a failed database save does not
# leave an incomplete registration in memory.
# Covers: Failure handling and inventory integrity.
# Expected: OSError and no newly registered asset.

def test_database_save_failure(client, physical_asset):
    from services import asset_service
    from models.asset_request import HardwareRegistrationRequest

    request = HardwareRegistrationRequest(**physical_asset)

    with patch.object(
        asset_service,
        "save_db",
        side_effect=OSError("Simulated database failure")
    ):
        with pytest.raises(
            OSError,
            match="Simulated database failure"
        ):
            asset_service.register_hardware(request)

    assert db_json.DB["hardware_assets"] == {}

