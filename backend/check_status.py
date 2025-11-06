#!/usr/bin/env python3
"""
Status Check Wrapper - Backward compatibility
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("ℹ️  Redirecting to scripts/check_status.py...")
print()

from scripts.check_status import check_status

if __name__ == "__main__":
    check_status()

