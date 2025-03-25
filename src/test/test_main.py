from unittest import TestCase

from fastapi.testclient import TestClient

from main import app


class MainTest(TestCase):

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_not_allowed_methods(self):
        not_allowed_methods = ("put", "get", "patch", "delete")
        for not_allowed_method in not_allowed_methods:
            with self.subTest(not_allowed_method):
                response = getattr(self.client, not_allowed_method)("/event")
                self.assertEqual(response.status_code, 405)
