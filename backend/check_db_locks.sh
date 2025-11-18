#!/bin/bash
# Script to check and kill processes locking the database

echo "Checking for database locks..."
DB_PATH="./data/database/telegram_jobs.db"

# Find processes using the database
echo "Processes accessing database:"
lsof "$DB_PATH" 2>/dev/null || fuser "$DB_PATH" 2>/dev/null || echo "No processes found (or lsof/fuser not available)"

echo ""
echo "To stop dashboard server:"
echo "  pkill -f 'web_dashboard.py'"
echo "  or"
echo "  killall python3  # (be careful, this kills all python processes)"

