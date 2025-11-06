#!/usr/bin/env python3
"""
Web Dashboard Wrapper
Redirects to dashboard/app.py for backward compatibility
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("ℹ️  Redirecting to dashboard/app.py...")
print()

# Import and run dashboard
from dashboard.app import app

if __name__ == '__main__':
    print("="*60)
    print("🌐 Starting Web Dashboard")
    print("="*60)
    print()
    print("Dashboard will open at: http://localhost:7000")
    print()
    print("Press Ctrl+C to stop")
    print("="*60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=7000)

