#! /bin/sh
# Start the uvicorn server
uvicorn main:app --reload --port "${PORT}" --host 0.0.0.0
