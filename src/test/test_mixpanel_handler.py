import unittest
from datetime import datetime
from unittest.mock import patch

from data_event import DataEvent
from mixpanel_handler import MixpanelEventSender


class MixpanelEventSenderTest(unittest.TestCase):

    def setUp(self) -> None:
        self.event = DataEvent()
        self.event.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        self.event.event_type = "test_event"
        self.event.user_identifier = "user_123"
        self.event.extra_info = "{'key': 'value'}"
        self.event.user_properties = "{'email': 'test@example.com', 'username': 'user_test'}"
        self.event.location = "{'city': 'Paparajote City'}"
        self.event.device = "{'model': 'PepePhone'}"

        self.expected_event_properties = {
            "key": "value",
            "time": self.event.timestamp,
        }
        self.expected_user_properties = {
            "city": "Paparajote City",
            "model": "PepePhone",
            "$email": "test@example.com",
            "$name": "user_test",
        }

    def test_parse_str_to_dict_valid(self):
        result = MixpanelEventSender._parse_str_to_dict("{'a': 1}")
        self.assertEqual(result, {"a": 1})

    def test_parse_str_to_dict_empty(self):
        result = MixpanelEventSender._parse_str_to_dict("None")
        self.assertEqual(result, {})

    def test_parse_str_to_dict_invalid(self):
        with self.assertLogs(level="ERROR") as log:
            result = MixpanelEventSender._parse_str_to_dict("{invalid}")
            self.assertEqual(result, {})
            self.assertTrue(any("Failed to parse event from string" in message for message in log.output))

    @patch("mixpanel_handler.Mixpanel")
    def test_send_event_normal(self, mock_mixpanel):
        self.event.event_type = "test_event"
        mock_mp_instance = mock_mixpanel.return_value

        MixpanelEventSender(self.event)

        expected_distinct_id = self.event.user_identifier or "unknown_user"
        mock_mp_instance.track.assert_called_once_with(
            distinct_id=expected_distinct_id,
            event_name=self.event.event_type,
            properties=self.expected_event_properties,
        )
        mock_mp_instance.people_set.assert_called_once_with(
            distinct_id=expected_distinct_id, properties=self.expected_user_properties
        )

    @patch("mixpanel_handler.Mixpanel")
    def test_send_event_rsync_user_properties_event(self, mock_mixpanel):
        self.event.event_type = "rsync_user_properties_event"
        mock_mp_instance = mock_mixpanel.return_value

        MixpanelEventSender(self.event)

        expected_distinct_id = self.event.user_identifier or "unknown_user"
        mock_mp_instance.track.assert_not_called()
        mock_mp_instance.people_set.assert_called_once_with(
            distinct_id=expected_distinct_id, properties=self.expected_user_properties
        )
