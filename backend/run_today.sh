#!/bin/bash

# 📅 Daily Run Script - रोज़ बस ये चलाओ!

clear
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║        🚀 Telegram Job Fetcher - Daily Run 🚀            ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📅 Date: $(date '+%d %B %Y, %A')"
echo "⏰ Time: $(date '+%I:%M %p')"
echo ""

# Check if it's working hours
HOUR=$(date +%H)
if [ $HOUR -lt 10 ] || [ $HOUR -ge 20 ]; then
    echo "⚠️  Not in working hours (10 AM - 8 PM)"
    echo "   Current time: $HOUR:00"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled. Come back during working hours!"
        exit 1
    fi
fi

echo "════════════════════════════════════════════════════════════"
echo "  📊 TODAY'S TASK"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Will do today:"
echo "  ✅ Join 8 new groups (2 per account)"
echo "  ✅ Fetch messages from all joined groups"
echo "  ✅ Extract company info & classify jobs"
echo "  ✅ Save to database & CSV"
echo "  ✅ NO duplicates (smart tracking)"
echo ""
echo "Time needed: ~2-3 hours"
echo "Laptop: Keep ON during this time"
echo ""

read -p "Start? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled."
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🔄 STARTING..."
echo "════════════════════════════════════════════════════════════"
echo ""

# Run the daily script
python3 daily_run.py

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ TODAY'S RUN COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 Check what was collected:"
echo "   python3 check_status.py"
echo ""
echo "📁 View files:"
echo "   Database: data/database/telegram_jobs.db"
echo "   CSV: data/csv/tech_jobs.csv"
echo "   Logs: logs/main_$(date +%Y%m%d).log"
echo ""
echo "💾 Data saved safely!"
echo "🔄 कल फिर से run करना!"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           ✨ Done! Laptop बंद कर सकते हो! ✨            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

