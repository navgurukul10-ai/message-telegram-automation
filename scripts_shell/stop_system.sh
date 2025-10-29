#!/bin/bash

# Telegram Job Fetcher - Stop Script

echo "═══════════════════════════════════════════════════════════"
echo "  🛑 Stopping Telegram Job Fetcher"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ ! -f pid.txt ]; then
    echo "⚠️  PID file not found. Is the system running?"
    echo ""
    echo "Checking for running processes..."
    ps aux | grep "python3 main.py" | grep -v grep
    exit 1
fi

PID=$(cat pid.txt)

if ps -p $PID > /dev/null 2>&1; then
    echo "📊 Found running process (PID: $PID)"
    echo "🛑 Stopping gracefully..."
    
    kill -SIGINT $PID
    
    sleep 2
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Process still running, forcing stop..."
        kill -9 $PID
    fi
    
    rm pid.txt
    echo "✅ System stopped successfully!"
else
    echo "⚠️  Process not running (PID: $PID)"
    rm pid.txt
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ SYSTEM STOPPED"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 To see what was collected:"
echo "   python3 check_status.py"
echo ""
echo "🚀 To restart:"
echo "   ./start_system.sh"
echo ""

