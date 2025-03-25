import ast

from mixpanel import Mixpanel

from data_event import DataEvent
from settings import MIXPANEL_PROJECT_TOKEN


def send_mixpanel_event(event: DataEvent):
    mp = Mixpanel(MIXPANEL_PROJECT_TOKEN)
    distinct_id = event.user_identifier if event.user_identifier else "unknown_user"
    if event.event_type != "rsync_user_properties_event":
        event_properties = {}
        event_properties_fields = []
        for field in event_properties_fields:
            value = getattr(event, field)
            if value:
                event_properties[field] = str(value)
        if event.extra_info and event.extra_info != "None":
            for key, value in ast.literal_eval(event.extra_info).items():
                event_properties[key] = str(value)
        event_properties["time"] = event.timestamp
        mp.track(distinct_id=distinct_id, event_name=event.event_type, properties=event_properties)
    user_properties = {}
    mixpanel_internal_user_properties = {
        "email": "$email",
        "first_name": "$first_name",
        "last_name": "$last_name",
        "avatar": "$avatar",
        "username": "$name",
    }
    if event.location and event.location != "None":
        for key, value in ast.literal_eval(event.location).items():
            if value:
                user_properties[key] = str(value)
    if event.device and event.device != "None":
        for key, value in ast.literal_eval(event.device).items():
            if value:
                user_properties[key] = str(value)
    if event.user_properties and event.user_properties != "None":
        for key, value in ast.literal_eval(event.user_properties).items():
            new_key = mixpanel_internal_user_properties.get(key, key)
            user_properties[new_key] = str(value)
    mp.people_set(
        distinct_id=distinct_id,
        properties=user_properties,
    )
