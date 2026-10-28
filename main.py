from database.db_json import load_db, save_db, DB
from models.asset_models import HardwareAsset, SoftwareLicence, AssetRetirement, AssetStatus, DisposalMethod


def seed_sample_data():
    """Populates the database with your sample dictionary records."""
    load_db()

    # Hardware Records
    hw1 = HardwareAsset(
        hardware_id="HW-10001",
        title="MacBook Pro 16",
        product="Laptop",
        warranty_expiry="2027-05-15",
        status=AssetStatus.ASSIGNED.value,
        assigned_employee_id="EMP-50001",
        department="Engineering",
        location="Headquarters",
        created_at="2026-10-28T09:00:00.000000",
        updated_at="2026-10-28T09:15:00.000000"
    )

    hw2 = HardwareAsset(
        hardware_id="HW-10002",
        title="Dell XPS 15",
        product="Laptop",
        warranty_expiry="2026-11-20",
        status=AssetStatus.AVAILABLE.value,
        assigned_employee_id=None,
        department="IT Support",
        location="Branch Office",
        created_at="2026-10-28T09:05:00.000000",
        updated_at="2026-10-28T09:05:00.000000"
    )

    hw3 = HardwareAsset(
        hardware_id="HW-10003",
        title="ThinkPad X1 Carbon",
        product="Laptop",
        warranty_expiry="2025-01-10",
        status=AssetStatus.RETIRED.value,
        assigned_employee_id=None,
        department="Finance",
        location="Headquarters",
        created_at="2024-01-10T08:00:00.000000",
        updated_at="2026-10-28T10:00:00.000000"
    )

    # Software Licences
    lic1 = SoftwareLicence(
        licence_id="LIC-20001",
        software_name="JetBrains PyCharm Professional",
        vendor="JetBrains",
        total_seats=5,
        assigned_employee_ids=["EMP-50001", "EMP-50002"],
        licence_key="XXXX-1234-YYYY-5678",
        expiry_date="2027-12-31",
        licence_type="Subscription",
        department="Software Engineering",
        created_at="2026-10-28T09:10:00.000000",
        updated_at="2026-10-28T09:20:00.000000"
    )

    lic2 = SoftwareLicence(
        licence_id="LIC-20002",
        software_name="Adobe Creative Cloud",
        vendor="Adobe",
        total_seats=2,
        assigned_employee_ids=["EMP-50003", "EMP-50004"],
        licence_key="ADBE-9999-CC00",
        expiry_date="2026-11-15",
        licence_type="Subscription",
        department="Design",
        created_at="2026-10-28T09:12:00.000000",
        updated_at="2026-10-28T09:25:00.000000"
    )

    # Asset Retirement
    ret1 = AssetRetirement(
        hardware_id="HW-10003",
        disposal_method=DisposalMethod.RECYCLED.value,
        disposal_date="2026-10-28",
        data_wipe_verified=True,
        retired_by_user_id="ADM-10001",
        retired_at="2026-10-28T10:00:00.000000"
    )

    # Insert into JSON Dictionary
    DB["hardware_assets"][hw1.hardware_id] = hw1.to_dict()
    DB["hardware_assets"][hw2.hardware_id] = hw2.to_dict()
    DB["hardware_assets"][hw3.hardware_id] = hw3.to_dict()

    DB["software_licences"][lic1.licence_id] = lic1.to_dict()
    DB["software_licences"][lic2.licence_id] = lic2.to_dict()

    DB["asset_retirements"][ret1.hardware_id] = ret1.to_dict()

    save_db()
    print("Database seeded and saved to database/itam_db.json successfully!")


if __name__ == "__main__":
    seed_sample_data()