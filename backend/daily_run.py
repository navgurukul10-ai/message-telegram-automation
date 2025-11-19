#!/usr/bin/env python3
"""
Daily Run Wrapper - Backward compatibility
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("ℹ️  Redirecting to scripts/daily_run.py...")
print()

from scripts.daily_run import daily_main
import asyncio

if __name__ == "__main__":
    asyncio.run(daily_main())

