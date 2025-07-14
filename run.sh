#!/bin/bash

# wget -qO- https://astral.sh/uv/install.sh | sh

if [ ! -d ".venv" ]; then
    echo ".venv not found. Running uv sync..."
    uv sync
    source .venv/bin/activate
fi

# This script starts the FastAPI application using uvicorn.
uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload