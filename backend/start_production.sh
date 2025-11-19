#!/bin/bash
# Production startup script for Telegram Jobs Backend

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create necessary directories
mkdir -p logs sessions data/database data/csv data/json

# Set environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Start with Gunicorn (production WSGI server)
# -w: number of worker processes (adjust based on CPU cores)
# -b: bind address and port
# --timeout: request timeout in seconds
# --access-logfile: access log file
# --error-logfile: error log file
gunicorn \
    -w 4 \
    -b 0.0.0.0:7000 \
    --timeout 120 \
    --access-logfile logs/gunicorn-access.log \
    --error-logfile logs/gunicorn-error.log \
    --log-level info \
    dashboard.app:app

