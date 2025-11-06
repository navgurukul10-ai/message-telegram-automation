#!/usr/bin/env python3
"""
Fix session file database locks by enabling WAL mode
Run this script to convert all session files to WAL mode
"""
import sqlite3
import os
from pathlib import Path

def fix_session_file(session_path):
    """Enable WAL mode for a session file"""
    try:
        print(f"Processing: {session_path.name}...")
        
        # Connect with timeout and enable WAL
        conn = sqlite3.connect(str(session_path), timeout=30.0)
        cursor = conn.cursor()
        
        # Check current mode
        cursor.execute("PRAGMA journal_mode;")
        current_mode = cursor.fetchone()[0]
        print(f"  Current mode: {current_mode}")
        
        # Enable WAL mode
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA busy_timeout=30000;")
        
        # Verify
        cursor.execute("PRAGMA journal_mode;")
        new_mode = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  ✅ New mode: {new_mode}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("SESSION FILE DATABASE LOCK FIX")
    print("="*60)
    print()
    
    sessions_dir = Path("sessions")
    
    if not sessions_dir.exists():
        print("❌ Sessions directory not found!")
        return 1
    
    # Find all .session files
    session_files = list(sessions_dir.glob("*.session"))
    
    if not session_files:
        print("❌ No session files found!")
        return 1
    
    print(f"Found {len(session_files)} session file(s)\n")
    
    success_count = 0
    for session_file in session_files:
        if fix_session_file(session_file):
            success_count += 1
        print()
    
    print("="*60)
    print(f"Results: {success_count}/{len(session_files)} session files fixed")
    print("="*60)
    
    if success_count == len(session_files):
        print("\n✅ All session files converted to WAL mode!")
        print("You can now run your system without database lock errors.")
        return 0
    else:
        print(f"\n⚠️  {len(session_files) - success_count} files failed.")
        print("Please check the errors above.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

