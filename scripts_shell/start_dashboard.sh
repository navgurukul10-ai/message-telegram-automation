#!/bin/bash

# Start Web Dashboard on Port 7000

clear
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║         🌐 Starting Web Dashboard 🌐                     ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Dashboard starting on port 7000..."
echo ""
echo "🌐 Open in browser:"
echo ""
echo "   ✨ http://localhost:7000 ✨"
echo ""
echo "   या"
echo ""
echo "   http://127.0.0.1:7000"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  💡 Dashboard Features:"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  ✅ Date-wise Groups Joined"
echo "  ✅ Date-wise Jobs (Tech/Non-Tech/Freelance)"
echo "  ✅ Best Verified Jobs"
echo "  ✅ Company Information"
echo "  ✅ Full Messages"
echo "  ✅ Real-time Updates"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Press Ctrl+C to stop"
echo "════════════════════════════════════════════════════════════"
echo ""

python3 web_dashboard.py

