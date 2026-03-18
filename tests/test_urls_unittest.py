# tests/test_urls_unittest.py
import os
import unittest
from flask import url_for
from app import create_app


class UrlMapTests(unittest.TestCase):
    def setUp(self):
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["DATABASE_URL"] = "sqlite:///test_unittest.db"

        self.app = create_app()
        self.app.config.update(TESTING=True)

    def test_tickets_list_endpoint_exists(self):
        with self.app.test_request_context():
            self.assertEqual(url_for("tickets.list"), "/")


if __name__ == "__main__":
    unittest.main(verbosity=2)