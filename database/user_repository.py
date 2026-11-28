"""JSON persistence for user accounts.
"""
import json
import os
from pathlib import Path
from threading import RLock

from models.user import User

DATABASE_DIR = Path(__file__).resolve().parent
USERS_LOCK = RLock()


def default_users_file() -> Path:
    # Looked up on every call so ITAM_DATA_DIR can be changed by tests or deployments.
    return Path(os.getenv("ITAM_DATA_DIR", DATABASE_DIR)) / "users.json"


class UserRepository:
    def __init__(self, file_path=None):
        self.file_path = Path(file_path) if file_path else default_users_file()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save([])

    def _load(self):
        with USERS_LOCK:
            try:
                with self.file_path.open("r", encoding="utf-8") as file:
                    records = json.load(file)
            except json.JSONDecodeError as exc:
                raise ValueError("The users data file contains invalid JSON.") from exc
        if not isinstance(records, list):
            raise ValueError("The users data file must contain a JSON list.")
        return [User.from_dict(record) for record in records]

    def _save(self, users):
        with USERS_LOCK:
            temporary_file = self.file_path.with_suffix(".tmp")
            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump([user.to_dict() for user in users], file, indent=4)
            temporary_file.replace(self.file_path)

    def get_all(self):
        return self._load()

    def get_by_id(self, user_id):
        try:
            wanted = int(user_id)
        except (TypeError, ValueError):
            return None
        return next((user for user in self._load() if user.user_id == wanted), None)

    def get_by_username(self, username):
        wanted = str(username or "").strip().casefold()
        return next((user for user in self._load() if user.username.casefold() == wanted), None)

    def add(self, user):
        with USERS_LOCK:
            users = self._load()
            users.append(user)
            self._save(users)
        return user

    def update(self, updated_user):
        with USERS_LOCK:
            users = self._load()
            for index, user in enumerate(users):
                if user.user_id == updated_user.user_id:
                    users[index] = updated_user
                    self._save(users)
                    return updated_user
        raise LookupError("User account was not found.")

    def replace_all(self, users):
        """Used by restore: swap the whole user list in one write."""
        self._save(list(users))

    def next_id(self):
        return max((user.user_id for user in self._load()), default=0) + 1
