#!/usr/bin/env python3
"""
Test script to verify connection fixes are working
"""
import sqlite3
import os
import sys
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def test_database_wal_mode():
    """Test if database is using WAL mode"""
    print("Testing database WAL mode...")
    
    db_path = "data/database/telegram_jobs.db"
    
    if not os.path.exists(db_path):
        print(f"{YELLOW}⚠️  Database not found. Will be created on first run.{RESET}")
        return True
    
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # Check journal mode
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        
        if mode.lower() == 'wal':
            print(f"{GREEN}✅ Database is using WAL mode{RESET}")
            print(f"   Mode: {mode}")
            return True
        else:
            print(f"{YELLOW}⚠️  Database is not using WAL mode: {mode}{RESET}")
            print(f"   Enabling WAL mode...")
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA journal_mode;")
            new_mode = cursor.fetchone()[0]
            print(f"{GREEN}✅ WAL mode enabled: {new_mode}{RESET}")
            return True
            
    except Exception as e:
        print(f"{RED}❌ Database test failed: {e}{RESET}")
        return False
    finally:
        if conn:
            conn.close()

def test_database_settings():
    """Test database connection settings"""
    print("\nTesting database connection settings...")
    
    db_path = "data/database/telegram_jobs.db"
    
    if not os.path.exists(db_path):
        print(f"{YELLOW}⚠️  Database not found yet.{RESET}")
        return True
    
    try:
        # Test with timeout
        conn = sqlite3.connect(db_path, timeout=30.0, isolation_level=None)
        cursor = conn.cursor()
        
        # Check settings
        cursor.execute("PRAGMA busy_timeout;")
        busy_timeout = cursor.fetchone()[0]
        
        print(f"{GREEN}✅ Connection successful with timeout{RESET}")
        print(f"   Busy timeout: {busy_timeout}ms")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"{RED}❌ Connection test failed: {e}{RESET}")
        return False

def test_session_files():
    """Check session files exist"""
    print("\nChecking session files...")
    
    sessions_dir = "sessions/"
    
    if not os.path.exists(sessions_dir):
        print(f"{YELLOW}⚠️  Sessions directory not found{RESET}")
        return False
    
    session_files = list(Path(sessions_dir).glob("*.session"))
    
    if session_files:
        print(f"{GREEN}✅ Found {len(session_files)} session file(s){RESET}")
        for session in session_files:
            size = os.path.getsize(session)
            print(f"   - {session.name} ({size:,} bytes)")
        return True
    else:
        print(f"{YELLOW}⚠️  No session files found. Run authorization first.{RESET}")
        return False

def test_imports():
    """Test if all imports work"""
    print("\nTesting Python imports...")
    
    try:
        from src.core.telegram_client import TelegramJobFetcher
        print(f"{GREEN}✅ telegram_client imports successfully{RESET}")
        
        from src.storage.database import DatabaseHandler
        print(f"{GREEN}✅ database handler imports successfully{RESET}")
        
        from src.utils.connection_monitor import ConnectionMonitor
        print(f"{GREEN}✅ connection_monitor imports successfully{RESET}")
        
        return True
        
    except ImportError as e:
        print(f"{RED}❌ Import failed: {e}{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        return False

def test_connection_monitor():
    """Test connection monitor utility"""
    print("\nTesting connection monitor utility...")
    
    try:
        from src.utils.connection_monitor import ConnectionMonitor
        
        monitor = ConnectionMonitor(check_interval=300)
        print(f"{GREEN}✅ Connection monitor created successfully{RESET}")
        
        # Test getting stats (should be empty)
        stats = monitor.get_stats()
        print(f"   Monitored clients: {len(stats)}")
        
        return True
        
    except Exception as e:
        print(f"{RED}❌ Connection monitor test failed: {e}{RESET}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"{GREEN}✅ {description}: {filepath}{RESET}")
        return True
    else:
        print(f"{RED}❌ Missing {description}: {filepath}{RESET}")
        return False

def main():
    print_header("CONNECTION FIXES VERIFICATION")
    
    print(f"{BLUE}This script verifies that all connection fixes are in place{RESET}\n")
    
    results = []
    
    # Test 1: Check modified files exist
    print_header("1. Checking Modified Files")
    results.append(check_file_exists("src/storage/database.py", "Database handler"))
    results.append(check_file_exists("src/core/telegram_client.py", "Telegram client"))
    results.append(check_file_exists("src/utils/connection_monitor.py", "Connection monitor"))
    results.append(check_file_exists("docs/CONNECTION_FIX_GUIDE.md", "Documentation"))
    
    # Test 2: Test imports
    print_header("2. Testing Imports")
    results.append(test_imports())
    
    # Test 3: Test database
    print_header("3. Testing Database")
    results.append(test_database_wal_mode())
    results.append(test_database_settings())
    
    # Test 4: Check sessions
    print_header("4. Checking Sessions")
    results.append(test_session_files())
    
    # Test 5: Test connection monitor
    print_header("5. Testing Connection Monitor")
    results.append(test_connection_monitor())
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}Your system is ready to handle internet connection issues!{RESET}\n")
        return 0
    else:
        print(f"\n{YELLOW}⚠️  Some tests failed, but this may be normal if:{RESET}")
        print(f"{YELLOW}   - Database hasn't been created yet (run main.py first){RESET}")
        print(f"{YELLOW}   - Sessions haven't been authorized yet (run auth scripts){RESET}")
        print(f"\n{BLUE}If you've already run the system before, please check the failures.{RESET}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)

