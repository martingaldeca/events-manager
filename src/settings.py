import os

from clickhouse_sqlalchemy import get_declarative_base, make_session
from sqlalchemy import create_engine

# Environment variables
API_KEY = os.environ.get("API_KEY", None)
PORT = int(os.environ.get("PORT", 8000))
PROJECT_NAME = os.environ.get("PROJECT_NAME", "default_project")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default_user")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "default_password")
CLICKHOUSE_DB = os.environ.get("CLICKHOUSE_DB", "default_db")
CLICKHOUSE_EXTERNAL_PORT = os.environ.get("CLICKHOUSE_EXTERNAL_PORT", "8123")
AMPLITUDE_API_KEY = os.environ.get("AMPLITUDE_API_KEY", None)
MIXPANEL_PROJECT_TOKEN = os.environ.get("MIXPANEL_PROJECT_TOKEN", None)

EVENT_TABLE_NAME = f"{PROJECT_NAME}_events"

# SQLAlchemy engine and session for ClickHouse
DATABASE_URL = (
    f"clickhouse://{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}@{PROJECT_NAME}_clickhouse:"
    f"{CLICKHOUSE_EXTERNAL_PORT}/{CLICKHOUSE_DB}"
)
engine = create_engine(DATABASE_URL)
SessionLocal = make_session(engine)
Base = get_declarative_base()
