#!/usr/bin/env python3
"""Quick test to verify client initialization works without database locks"""
import asyncio
import sys
sys.path.insert(0, '.')

from src.core.telegram_client import TelegramJobFetcher

async def test_init():
    print("="*60)
    print("Testing Client Initialization (No Database Locks)")
    print("="*60)
    print()
    
    try:
        fetcher = TelegramJobFetcher()
        print("✅ TelegramJobFetcher created")
        print()
        
        print("Initializing clients (this will take ~15 seconds)...")
        await fetcher.initialize_clients()
        
        print()
        print("="*60)
        print(f"✅ SUCCESS! Initialized {len(fetcher.clients)} clients")
        print("="*60)
        
        # Cleanup
        print("\nCleaning up...")
        await fetcher.close_clients()
        print("✅ All clients closed cleanly")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(test_init()))
