#!/usr/bin/env python3
"""
Quick Connection Test
Tests if the timeout fix is working
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.telegram_client import TelegramJobFetcher
from src.utils.logger import get_logger

logger = get_logger('connection_test')

async def test_connection():
    """Test if clients can connect successfully"""
    print("="*70)
    print("  🔧 TESTING CONNECTION AFTER TIMEOUT FIX")
    print("="*70)
    print()
    
    try:
        print("📡 Initializing Telegram clients with new timeout settings...")
        print()
        
        fetcher = TelegramJobFetcher()
        
        # Try to initialize clients
        await fetcher.initialize_clients()
        
        if not fetcher.clients:
            print("❌ FAILED: No clients initialized")
            print()
            print("Possible reasons:")
            print("  1. Network is still unstable")
            print("  2. Need to authorize accounts")
            print("  3. config.py not set up correctly")
            print()
            print("Try:")
            print("  python3 scripts/check_auth.py")
            return False
        
        print()
        print("="*70)
        print(f"  ✅ SUCCESS! Connected {len(fetcher.clients)} accounts")
        print("="*70)
        print()
        
        # Show connected accounts
        for i, client_info in enumerate(fetcher.clients, 1):
            account = client_info['account']
            print(f"  Account {i}: {account['name']}")
            try:
                me = await client_info['client'].get_me()
                print(f"    └─ Name: {me.first_name} {me.last_name or ''}")
                print(f"    └─ Phone: {account['phone']}")
                print(f"    └─ Status: ✅ Connected")
            except Exception as e:
                print(f"    └─ Status: ⚠️  Connected but couldn't get info ({e})")
            print()
        
        # Cleanup
        await fetcher.close_clients()
        
        print("="*70)
        print("  🎉 CONNECTION TEST PASSED!")
        print("="*70)
        print()
        print("  You can now run:")
        print("    python3 scripts/daily_run.py")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("="*70)
        print("  ❌ CONNECTION TEST FAILED")
        print("="*70)
        print()
        print(f"  Error: {e}")
        print()
        print("  Troubleshooting steps:")
        print("    1. Check your internet connection")
        print("    2. Read TIMEOUT_FIX.md for detailed solutions")
        print("    3. Try: ping -c 5 149.154.167.50")
        print("    4. Check if accounts are authorized:")
        print("       python3 scripts/check_auth.py")
        print()
        logger.error(f"Connection test failed: {e}", exc_info=True)
        return False
    
    finally:
        # Make sure to cleanup
        if 'fetcher' in locals():
            try:
                await fetcher.close_clients()
            except:
                pass

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)


