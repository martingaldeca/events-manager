import logging
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

import settings
from data_event import (
    DataEvent,  # Ensure your ClickHouse model includes the proper engine configuration
)
from security import api_key_auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.API_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from settings import Base, engine

    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Events manager", lifespan=lifespan)


class PostedEvent(BaseModel):
    timestamp: str
    event_type: str
    user_identifier: Optional[str] = None
    extra_info: Optional[dict] = None
    user_properties: Optional[dict] = None
    app_version: Optional[str] = None
    location: Optional[dict] = None
    device: Optional[dict] = None


class EventResultResult(BaseModel):
    event_received: Optional[bool] = None
    event_error: Optional[str] = None


@app.post("/event", dependencies=[Security(api_key_auth)], response_model=EventResultResult)
async def create_event(posted_event: PostedEvent):
    event_error = None
    try:
        DataEvent(posted_event=posted_event).save()
    except Exception as ex:
        logging.error(ex)
        event_error = str(ex)
    response = {
        "event_received": True,
        "event_error": event_error,
    }
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
