import logging
from datetime import datetime

from clickhouse_sqlalchemy import engines, types
from sqlalchemy import Column, DateTime, String, literal_column

from settings import EVENT_TABLE_NAME, Base, SessionLocal


class DataEvent(Base):
    __tablename__ = EVENT_TABLE_NAME

    timestamp = Column(DateTime, nullable=False, primary_key=True)
    event_type = Column(String, nullable=False, primary_key=True)
    user_identifier = Column(String, nullable=True)
    extra_info = Column(String, nullable=True)
    user_properties = Column(String, nullable=True)
    app_version = Column(String, nullable=True)
    location = Column(String, nullable=True)
    device = Column(String, nullable=True)
    mixpanel_uploaded = Column(types.UInt8, default=0)
    version = Column(DateTime, nullable=False)

    __table_args__ = (
        engines.ReplacingMergeTree(
            order_by=["timestamp", "event_type"],
            partition_by=literal_column("toYYYYMM(timestamp)"),
        ),
    )

    def __init__(self, posted_event=None, **kwargs):
        super().__init__(**kwargs)
        if posted_event:
            self.timestamp = datetime.strptime(posted_event.timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
            self.event_type = posted_event.event_type
            self.user_identifier = posted_event.user_identifier
            self.extra_info = str(posted_event.extra_info) if posted_event.extra_info else None
            self.user_properties = str(posted_event.user_properties) if posted_event.user_properties else None
            self.app_version = posted_event.app_version
            self.location = str(posted_event.location) if posted_event.location else None
            self.device = str(posted_event.device) if posted_event.device else None
            self.version = datetime.now()

    def save(self):
        try:
            from mixpanel_handler import MixpanelEventSender

            MixpanelEventSender(event=self)
            self.mixpanel_uploaded = 1
        except Exception as ex:
            logging.error("Failed to log event to Mixpanel: %s", str(ex))
            self.mixpanel_uploaded = 0
        session = SessionLocal
        try:
            session.add(self)
            session.commit()
        except Exception as ex:
            logging.error("Failed to save event in database: %s", str(ex))
        finally:
            session.close()

    @classmethod
    def table_name(cls):
        return EVENT_TABLE_NAME

    def __str__(self):
        return f"{self.event_type} - {self.user_identifier} - {self.version}"

    def __repr__(self):
        return str(self)
