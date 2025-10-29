#!/usr/bin/env python3
"""
Daily Run Script - Run job collection for one day
"""
import os
import sys
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.telegram_client import TelegramJobFetcher
from src.utils.logger import get_logger

logger = get_logger('daily_run')

async def daily_main():
    """Run daily job collection"""
    print("🚀 Starting Daily Job Collection...")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Initialize the job fetcher
        fetcher = TelegramJobFetcher()
        
        # Start the collection process (run for 1 day)
        await fetcher.run_continuous(duration_days=1)
        
        print("✅ Daily collection completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Collection stopped by user")
    except Exception as e:
        print(f"❌ Error during collection: {e}")
        logger.error(f"Daily run error: {e}")

if __name__ == "__main__":
    asyncio.run(daily_main())

