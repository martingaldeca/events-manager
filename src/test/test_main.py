import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from security import api_key_auth


class MainTest(unittest.TestCase):

    def setUp(self) -> None:
        self.client = TestClient(app)
        app.dependency_overrides[api_key_auth] = lambda: "test"

    def tearDown(self) -> None:
        app.dependency_overrides = {}

    def test_not_allowed_methods(self):
        not_allowed_methods = ("put", "get", "patch", "delete")
        for method in not_allowed_methods:
            with self.subTest(method=method):
                response = getattr(self.client, method)("/event")
                self.assertEqual(response.status_code, 405)

    @patch("main.DataEvent")
    def test_create_event_calls_save(self, mock_data_event):
        payload = {"timestamp": "2021-01-01T00:00:00", "event_type": "test_event"}
        instance = mock_data_event.return_value
        instance.save.return_value = None
        response = self.client.post("/event", json=payload)
        self.assertEqual(response.status_code, 200)
        instance.save.assert_called_once()
        json_response = response.json()
        self.assertTrue(json_response.get("event_received"))
        self.assertIsNone(json_response.get("event_error"))
        app.dependency_overrides.pop(api_key_auth, None)

    @patch("logging.error")
    @patch("main.DataEvent")
    def test_create_event_handles_exception(self, mock_data_event, _):
        payload = {"timestamp": "2021-01-01T00:00:00", "event_type": "test_event"}
        instance = mock_data_event.return_value
        instance.save.side_effect = Exception("Test exception")
        response = self.client.post("/event", json=payload)
        self.assertEqual(response.status_code, 200)
        instance.save.assert_called_once()
        json_response = response.json()
        self.assertTrue(json_response.get("event_received"))
        self.assertEqual(json_response.get("event_error"), "Test exception")
        app.dependency_overrides.pop(api_key_auth, None)
