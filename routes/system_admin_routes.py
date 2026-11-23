"""Business logic for System Administrator user-account tasks."""
import re
from models.user import User
from database.user_repository import UserRepository

VALID_ROLES = {
    "Asset Manager",
    "Employee",
    "System Administrator",
    "Auditor",
}

class UserService:
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    @staticmethod
    def _validate(username, full_name, email, role):
        if not all(str(value).strip() for value in (username, full_name, email, role)):
            raise ValueError("All fields are required.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            raise ValueError("Please enter a valid email address.")
        if role.strip() not in VALID_ROLES:
            raise ValueError("Please select a valid system role.")

    def list_users(self):
        return self.repository.get_all()

    def get_user(self, user_id):
        return self.repository.get_by_id(user_id)

    # US-SA-01: Create a user account
    def create_user(self, username, full_name, email, role):
        self._validate(username, full_name, email, role)
        users = self.repository.get_all()
        if any(u.username.casefold() == username.strip().casefold() for u in users):
            raise ValueError("That username is already in use.")

        user = User(
            user_id=self.repository.next_id(),
            username=username.strip(),
            full_name=full_name.strip(),
            email=email.strip(),
            role=role.strip(),
            active=True,
        )
        return self.repository.add(user)

    # US-SA-02: Edit user account details
    def update_user(self, user_id, username, full_name, email, role):
        existing = self.repository.get_by_id(user_id)
        if existing is None:
            raise LookupError("User account was not found.")

        self._validate(username, full_name, email, role)
        for user in self.repository.get_all():
            if user.user_id != existing.user_id and user.username.casefold() == username.strip().casefold():
                raise ValueError("That username is already in use.")

        existing.username = username.strip()
        existing.full_name = full_name.strip()
        existing.email = email.strip()
        existing.role = role.strip()
        return self.repository.update(existing)

    # US-SA-03: Deactivate a user account (retain the record)
    def deactivate_user(self, user_id):
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise LookupError("User account was not found.")
        user.active = False
        return self.repository.update(user)
