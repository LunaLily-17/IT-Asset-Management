import json
import os
from pathlib import Path
from threading import RLock

DB_FILE_PATH = Path(__file__).resolve().parent / "itam_db.json"
COLLECTIONS = (
    "hardware_assets",
    "software_assets",
    "software_licences",
    "asset_retirements",
    "employees",
    "asset_assignments",
    "audit_logs")
DB: dict = {name: {} for name in COLLECTIONS}
DB_LOCK = RLock()  # protects this process only, not multiple server workers


def load_db() -> dict:
    with DB_LOCK:
        path = Path(DB_FILE_PATH)
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            if not isinstance(loaded, dict):
                raise ValueError("Database root must be an object")
            for collection in COLLECTIONS:
                loaded.setdefault(collection, {})
                if not isinstance(loaded[collection], dict):
                    raise ValueError(f"Database collection {collection} must be an object")
            DB.clear()
            DB.update(loaded)
        else:
            DB.clear()
            DB.update({name: {} for name in COLLECTIONS})
            save_db()
        return DB


def save_db() -> None:
    with DB_LOCK:
        path = Path(DB_FILE_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        try:
            with temporary.open("w", encoding="utf-8") as handle:
                json.dump(DB, handle, indent=2, allow_nan=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
