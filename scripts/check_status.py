#!/usr/bin/env python3
"""
Status Check Script - Check system status
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PATHS, DATABASE
from src.utils.logger import get_logger

logger = get_logger('check_status')

def check_status():
    """Check system status and display statistics"""
    print("🔍 Checking System Status...")
    print("=" * 50)
    
    # Check database
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    if os.path.exists(db_path):
        print("✅ Database found")
        
        # Get statistics
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📊 Tables: {len(tables)}")
            
            # Count jobs
            for table in ['tech_jobs', 'non_tech_jobs', 'freelance_jobs']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   {table}: {count} jobs")
                except:
                    print(f"   {table}: Table not found")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print("❌ Database not found")
    
    # Check logs
    log_dir = PATHS['logs']
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        print(f"📝 Log files: {len(log_files)}")
    else:
        print("❌ Logs directory not found")
    
    # Check sessions
    session_dir = PATHS['sessions']
    if os.path.exists(session_dir):
        session_files = [f for f in os.listdir(session_dir) if f.endswith('.session')]
        print(f"🔐 Session files: {len(session_files)}")
    else:
        print("❌ Sessions directory not found")
    
    print("=" * 50)
    print("✅ Status check complete")

if __name__ == "__main__":
    check_status()

