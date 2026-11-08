#!/usr/bin/env bash
set -e

MODE="${1:---api}"

if [ "$MODE" == "--web" ]; then
    echo "Starting ADK Web UI on http://localhost:8000..."
    adk web .
else
    echo "Starting FastAPI Qualification Service on http://localhost:8080..."
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
fi
