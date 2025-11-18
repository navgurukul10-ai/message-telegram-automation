#!/bin/bash

# Script to check for running processes that might conflict with daily_run.py

echo "============================================================"
echo "🔍 Checking for running processes..."
echo "============================================================"

# Check for web_dashboard.py
DASHBOARD_PIDS=$(pgrep -f "web_dashboard.py|dashboard/app.py")
if [ -n "$DASHBOARD_PIDS" ]; then
    echo "⚠️  WARNING: Dashboard server is running (PIDs: $DASHBOARD_PIDS)"
    echo "   This can cause 'database is locked' errors!"
    echo "   To stop: pkill -f 'web_dashboard.py|dashboard/app.py'"
else
    echo "✅ No dashboard server running"
fi

# Check for daily_run.py
DAILY_PIDS=$(pgrep -f "daily_run.py")
if [ -n "$DAILY_PIDS" ]; then
    echo "ℹ️  daily_run.py is running (PIDs: $DAILY_PIDS)"
else
    echo "✅ No daily_run.py running"
fi

# Check for database locks
DB_PATH="/home/ng/finals/message-telegram-automation/backend/data/database/telegram_jobs.db"
if [ -f "${DB_PATH}-wal" ]; then
    echo "✅ Database is in WAL mode (allows concurrent access)"
else
    echo "⚠️  Database is NOT in WAL mode"
fi

# Check for processes accessing the database
DB_ACCESS=$(lsof "$DB_PATH" 2>/dev/null | grep -v COMMAND)
if [ -n "$DB_ACCESS" ]; then
    echo "ℹ️  Processes accessing database:"
    echo "$DB_ACCESS"
else
    echo "✅ No processes currently accessing database"
fi

echo ""
echo "============================================================"
echo "💡 Recommendation:"
echo "   Stop dashboard before running daily_run.py to avoid locks"
echo "   Command: pkill -f 'web_dashboard.py|dashboard/app.py'"
echo "============================================================"


