#!/bin/bash

# Telegram Job Fetcher - Start Script
# यह script system को background में 30 दिन के लिए चलाएगी

echo "═══════════════════════════════════════════════════════════"
echo "  🚀 Starting Telegram Job Fetcher"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if already running
if [ -f pid.txt ]; then
    PID=$(cat pid.txt)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  System is already running (PID: $PID)"
        echo ""
        echo "To stop: kill -SIGINT $PID"
        echo "To check status: python3 check_status.py"
        exit 1
    fi
fi

echo "📋 Configuration:"
echo "   Duration: 30 days"
echo "   Working hours: 10 AM - 8 PM"
echo "   Groups/day: 8 (2 per account)"
echo "   Check interval: Every 1 hour"
echo ""

echo "🔄 Starting in background..."
nohup python3 main.py > output.log 2>&1 &
PID=$!
echo $PID > pid.txt

echo "✅ System started successfully!"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 SYSTEM INFORMATION"
echo "═══════════════════════════════════════════════════════════"
echo "Process ID: $PID"
echo "Output log: output.log"
echo "System logs: logs/main_$(date +%Y%m%d).log"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🔍 MONITORING COMMANDS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Check status:"
echo "  python3 check_status.py"
echo ""
echo "View live logs:"
echo "  tail -f logs/main_$(date +%Y%m%d).log"
echo ""
echo "View output:"
echo "  tail -f output.log"
echo ""
echo "Check if running:"
echo "  ps aux | grep main.py"
echo ""
echo "Stop system:"
echo "  kill -SIGINT $(cat pid.txt)"
echo "  # or"
echo "  ./stop_system.sh"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✨ System will run for 30 days automatically!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🎉 Done! System is running in background."
echo "    Terminal बंद कर सकते हो, system चलता रहेगा!"
echo ""

