import unittest
from unittest.mock import MagicMock, patch

from data_event import DataEvent
from main import PostedEvent


class DataEventTest(unittest.TestCase):

    def setUp(self) -> None:
        self.posted_event = PostedEvent(
            timestamp="2023-01-01T12:00:00",
            event_type="test_event",
            user_identifier="user_123",
            extra_info={"key": "value"},
            user_properties={"prop": "value"},
            app_version="1.0",
            location={"lat": "10", "lon": "20"},
            device={"type": "mobile"},
        )

    @patch("data_event.SessionLocal", new_callable=MagicMock)
    @patch("mixpanel_handler.MixpanelEventSender")
    def test_save_success(self, mock_mixpanel, mock_session):
        data_event = DataEvent(posted_event=self.posted_event)
        data_event.save()

        mock_mixpanel.assert_called_once_with(event=data_event)
        self.assertEqual(data_event.mixpanel_uploaded, 1)
        mock_session.add.assert_called_once_with(data_event)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("data_event.SessionLocal", new_callable=MagicMock)
    @patch("mixpanel_handler.MixpanelEventSender", side_effect=Exception("Mixpanel error"))
    def test_save_mixpanel_failure(self, mock_mixpanel, mock_session):
        data_event = DataEvent(posted_event=self.posted_event)
        data_event.save()

        self.assertEqual(data_event.mixpanel_uploaded, 0)
        mock_mixpanel.assert_called_once_with(event=data_event)
        mock_session.add.assert_called_once_with(data_event)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
