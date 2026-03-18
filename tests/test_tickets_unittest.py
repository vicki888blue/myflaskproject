# tests/test_tickets_unittest.py
import os
import unittest
from unittest.mock import patch
from app import create_app
import tickets.routes as tickets_routes


class TicketsTests(unittest.TestCase):
    def setUp(self):
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["DATABASE_URL"] = "sqlite:///test_unittest.db"

        self.app = create_app()
        self.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = self.app.test_client()

    def test_ticket_list_requires_login(self):
        res = self.client.get("/", follow_redirects=False)
        # IF not logged in → redirect to /login
        self.assertIn(res.status_code, (302, 303))
        self.assertIn("/login", res.headers["Location"])

    def test_ticket_list_loads_when_logged_in(self):
        with patch.object(tickets_routes.repo, "list_tickets", return_value=[]):
            with self.client.session_transaction() as sess:
                sess["user_id"] = 1
                sess["username"] = "victoria"
                sess["role_id"] = 3

            res = self.client.get("/")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"ticket", res.data.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)