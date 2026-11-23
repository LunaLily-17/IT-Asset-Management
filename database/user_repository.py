"""JSON persistence for user accounts.

This repository keeps persistence separate from business rules. If the team already
has a database implementation, replace this class with an adapter to that database
while preserving the methods used by UserService.
"""
import json
from pathlib import Path
from models.user import User

DEFAULT_FILE = Path(__file__).resolve().parent / "users.json"

class UserRepository:
    def __init__(self, file_path=DEFAULT_FILE):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save([])

    def _load(self):
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                records = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError("The users data file contains invalid JSON.") from exc
        if not isinstance(records, list):
            raise ValueError("The users data file must contain a JSON list.")
        return [User.from_dict(record) for record in records]

    def _save(self, users):
        temporary_file = self.file_path.with_suffix(".tmp")
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump([user.to_dict() for user in users], file, indent=4)
        temporary_file.replace(self.file_path)

    def get_all(self):
        return self._load()

    def get_by_id(self, user_id):
        return next((user for user in self._load() if user.user_id == int(user_id)), None)

    def add(self, user):
        users = self._load()
        users.append(user)
        self._save(users)
        return user

    def update(self, updated_user):
        users = self._load()
        for index, user in enumerate(users):
            if user.user_id == updated_user.user_id:
                users[index] = updated_user
                self._save(users)
                return updated_user
        raise LookupError("User account was not found.")

    def next_id(self):
        return max((user.user_id for user in self._load()), default=0) + 1
