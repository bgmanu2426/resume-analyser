#!/bin/bash

# This script starts the FastAPI application using uvicorn.
uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload