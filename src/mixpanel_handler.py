import ast
import logging

from mixpanel import Mixpanel

from data_event import DataEvent
from settings import MIXPANEL_PROJECT_TOKEN


class MixpanelEventSender:
    def __init__(self, event: DataEvent, project_token: str = MIXPANEL_PROJECT_TOKEN) -> None:
        self.mp = Mixpanel(project_token)
        self.event = event
        self.send_event()

    @staticmethod
    def _parse_str_to_dict(s: str) -> dict:
        # Safely parse a string into a dictionary.
        try:
            return ast.literal_eval(s) if s and s != "None" else {}
        except Exception as ex:
            logging.error("Failed to parse event from string: %s", str(ex))
            return {}

    def _extract_event_properties(self) -> dict:
        properties = {}
        extra_info = self._parse_str_to_dict(self.event.extra_info)
        properties.update({key: str(value) for key, value in extra_info.items() if value})
        properties["time"] = self.event.timestamp
        return properties

    def _extract_user_properties(self) -> dict:
        user_properties = {}
        internal_mapping = {
            "email": "$email",
            "first_name": "$first_name",
            "last_name": "$last_name",
            "avatar": "$avatar",
            "username": "$name",
        }

        for prop_str in (self.event.location, self.event.device):
            props = self._parse_str_to_dict(prop_str)
            user_properties.update({key: str(value) for key, value in props.items() if value})

        user_props = self._parse_str_to_dict(self.event.user_properties)
        for key, value in user_props.items():
            if value:
                mapped_key = internal_mapping.get(key, key)
                user_properties[mapped_key] = str(value)
        return user_properties

    def send_event(self) -> None:
        distinct_id = self.event.user_identifier or "unknown_user"

        if self.event.event_type != "rsync_user_properties_event":
            event_properties = self._extract_event_properties()
            self.mp.track(
                distinct_id=distinct_id,
                event_name=self.event.event_type,
                properties=event_properties,
            )

        user_properties = self._extract_user_properties()
        self.mp.people_set(
            distinct_id=distinct_id,
            properties=user_properties,
        )
