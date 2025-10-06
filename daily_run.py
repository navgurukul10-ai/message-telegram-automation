"""
Daily Run Script - Run for one day at a time
Modified version that runs for just today instead of 30 days
"""
import asyncio
import sys
from datetime import datetime
from telegram_client import TelegramJobFetcher
from utils.logger import get_logger

logger = get_logger('daily_run')

async def daily_main():
    """Run fetcher for today only"""
    try:
        logger.info("="*60)
        logger.info("Telegram Job Fetcher - DAILY MODE")
        logger.info("="*60)
        
        # Initialize fetcher
        fetcher = TelegramJobFetcher()
        
        # Initialize clients
        logger.info("Initializing Telegram clients...")
        await fetcher.initialize_clients()
        
        if not fetcher.clients:
            logger.error("No clients initialized. Exiting...")
            return
        
        logger.info(f"Running for TODAY only (check every hour)")
        logger.info(f"Working hours: 10 AM - 8 PM")
        logger.info(f"Groups limit: 8 groups today")
        logger.info(f"You can run this script daily for continuous operation")
        
        # Run for just 1 day
        await fetcher.run_continuous(duration_days=1)
        
        logger.info("Today's fetching completed!")
        logger.info("Run again tomorrow to continue!")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down...")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    
    finally:
        # Cleanup
        if 'fetcher' in locals():
            await fetcher.close_clients()
        
        logger.info("="*60)
        logger.info("Daily run completed")
        logger.info("="*60)

if __name__ == "__main__":
    asyncio.run(daily_main())

