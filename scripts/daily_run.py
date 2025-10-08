"""
Daily Run Script - Run for one day at a time
Modified version that runs for just today instead of 30 days
Includes automatic maintenance: job type fixing and CSV sync
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.telegram_client import TelegramJobFetcher
from src.utils.logger import get_logger
from src.utils.maintenance import perform_maintenance

logger = get_logger('daily_run')

async def daily_main():
    """Run fetcher for today only with automatic maintenance"""
    try:
        logger.info("="*60)
        logger.info("Telegram Job Fetcher - DAILY MODE")
        logger.info("="*60)
        
        # Step 1: Perform maintenance (fix job types + sync CSV)
        logger.info("Performing automatic maintenance...")
        maintenance_results = perform_maintenance()
        
        if maintenance_results:
            fixed = maintenance_results.get('job_types_fixed', 0)
            if fixed > 0:
                logger.info(f"✅ Fixed {fixed} empty job types")
            
            csv_sync = maintenance_results.get('csv_sync', {})
            if csv_sync:
                logger.info(f"✅ CSV files synced with database")
        
        # Step 2: Initialize fetcher
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
        
        # Step 3: Run for just 1 day
        await fetcher.run_continuous(duration_days=1)
        
        # Step 4: Final maintenance after fetching
        logger.info("Performing final CSV sync...")
        perform_maintenance()
        
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

