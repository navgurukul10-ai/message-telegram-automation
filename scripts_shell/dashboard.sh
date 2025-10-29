#!/bin/bash
# Dashboard Wrapper - Easy command!
cd "$(dirname "$0")/.."
echo "🌐 Starting Dashboard on http://localhost:7001"
python3 web/app.py

