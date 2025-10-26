#!/bin/bash
# Startup script for Railway deployment
# This properly handles the $PORT environment variable

# Use Railway's PORT or default to 8000
PORT=${PORT:-8000}

echo "Starting webhook server on port $PORT"
exec python -m uvicorn api.webhook_server:app --host 0.0.0.0 --port $PORT
