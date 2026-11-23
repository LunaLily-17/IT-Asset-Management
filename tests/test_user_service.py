import tempfile
import unittest
from pathlib import Path

from database.user_repository import UserRepository
from services.user_service import UserService

class UserServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        repository = UserRepository(Path(self.temp_dir.name) / "users.json")
        self.service = UserService(repository)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_sample(self):
        return self.service.create_user(
            "jane", "Jane Smith", "jane@example.com", "Employee"
        )

    def test_sa01_create_user(self):
        user = self.create_sample()
        self.assertEqual(user.user_id, 1)
        self.assertTrue(user.active)

    def test_sa01_reject_duplicate_username(self):
        self.create_sample()
        with self.assertRaises(ValueError):
            self.service.create_user(
                "JANE", "Jane Jones", "jane2@example.com", "Employee"
            )

    def test_sa01_reject_invalid_email_and_role(self):
        with self.assertRaises(ValueError):
            self.service.create_user("bob", "Bob", "not-an-email", "Employee")
        with self.assertRaises(ValueError):
            self.service.create_user("bob", "Bob", "bob@example.com", "Unknown")

    def test_sa02_edit_user(self):
        user = self.create_sample()
        changed = self.service.update_user(
            user.user_id, "jane.s", "Jane Smith", "jane.s@example.com", "Auditor"
        )
        self.assertEqual(changed.username, "jane.s")
        self.assertEqual(changed.role, "Auditor")

    def test_sa02_unknown_user(self):
        with self.assertRaises(LookupError):
            self.service.update_user(99, "nobody", "Nobody", "n@example.com", "Employee")

    def test_sa03_deactivate_user_retains_record(self):
        user = self.create_sample()
        changed = self.service.deactivate_user(user.user_id)
        self.assertFalse(changed.active)
        self.assertEqual(len(self.service.list_users()), 1)

    def test_sa03_unknown_user(self):
        with self.assertRaises(LookupError):
            self.service.deactivate_user(99)

if __name__ == "__main__":
    unittest.main()
