# tests/test_auth_unittest.py
import os
import unittest
from unittest.mock import patch
from app import create_app
import auth.routes as auth_routes


class AuthTests(unittest.TestCase):
    def setUp(self):
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["DATABASE_URL"] = "sqlite:///test_unittest.db"

        self.app = create_app()
        self.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = self.app.test_client()

    def test_login_page_loads(self):
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"login", res.data.lower())

    def test_login_invalid_credentials_redirects(self):
        with patch.object(auth_routes, "authenticate", return_value=None):
            res = self.client.post(
                "/login",
                data={"username_or_email": "x", "password": "y"},
                follow_redirects=False
            )
        self.assertIn(res.status_code, (302, 303))
        self.assertIn("/login", res.headers["Location"])

    def test_login_success_redirects_to_ticket_list(self):
        fake_user = {"id": 1, "username": "victoria", "role_id": 3}

        with patch.object(auth_routes, "authenticate", return_value=fake_user):
            res = self.client.post(
                "/login",
                data={"username_or_email": "victoria", "password": "pw"},
                follow_redirects=False
            )

        # YOUR ROUTE → list_tickets() is mounted at "/"
        self.assertIn(res.status_code, (302, 303))
        self.assertIn("/", res.headers["Location"])


if __name__ == "__main__":
    unittest.main(verbosity=2)