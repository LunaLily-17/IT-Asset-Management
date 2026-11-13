import json
import os
from typing import Dict, Any

DB_FILE_PATH = "database/itam_db.json"

# In-Memory Global Database Instance
DB: Dict[str, Any] = {
    "hardware_assets": {},
    "software_licences": {},
    "asset_retirements": {}
}


def load_db() -> Dict[str, Any]:
    """Loads JSON file into memory."""
    global DB
    if os.path.exists(DB_FILE_PATH):
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            DB = json.load(f)
    else:
        save_db()  # Initialize empty file
    return DB


def save_db():
    """Saves current memory state to JSON file."""
    os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
    with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(DB, f, indent=2)