
import pytest
from unittest.mock import patch

from database import db_json
from models.asset_request import AssetRegistrationRequest
from services import asset_service


# TC15 - Database Save Failure
# Purpose: Execute the exception/rollback path.
# Technique: White-box / Branch Coverage
# Expected: OSError and no asset remaining in memory.
def test_database_save_failure(client, physical_asset):
    request = AssetRegistrationRequest(**physical_asset)

    with patch.object(
        asset_service,
        "save_db",
        side_effect=OSError("Simulated database failure")
    ):
        with pytest.raises(OSError):
            asset_service.register_asset(request)

    assert db_json.DB["assets"] == {}


# TC16 - Unknown Asset ID
# Purpose: Exercise the not-found route branch.
# Technique: White-box / Branch Coverage
# Expected: HTTP 404.
def test_unknown_asset(client):
    response = client.get("/assets/AST-UNKNOWN")

    assert response.status_code == 404


# TC17 - Valid Registration Path
# Purpose: Exercise the successful registration path.
# Technique: White-box / Branch Coverage
# Expected: Asset created and retrievable.
def test_successful_registration(client, software_asset):
    created = client.post("/assets", json=software_asset)

    assert created.status_code == 201

    asset_id = created.json()["asset_id"]
    retrieved = client.get(f"/assets/{asset_id}")

    assert retrieved.status_code == 200
    assert retrieved.json()["asset_id"] == asset_id
