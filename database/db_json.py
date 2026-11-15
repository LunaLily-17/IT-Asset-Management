
import json
import os
from pathlib import Path
from typing import Dict, Any


DB_FILE_PATH = (
    Path(__file__).resolve().parent / "itam_db.json"
)

DB: Dict[str, Any] = {
    "hardware_assets": {},
    "software_licences": {},
    "asset_retirements": {}
}


def load_db() -> Dict[str, Any]:
    """Load saved data into the shared dictionary."""

    if os.path.exists(DB_FILE_PATH):
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid database structure")

        DB.clear()
        DB.update(data)

        DB.setdefault("hardware_assets", {})
        DB.setdefault("software_licences", {})
        DB.setdefault("asset_retirements", {})
    else:
        save_db()

    return DB


def save_db():
    """Persist the shared database to JSON."""

    path = Path(DB_FILE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file before replacing
    temp_path = path.with_name(path.name + ".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(DB, f, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, path)

    finally:
        if temp_path.exists():
            temp_path.unlink()
