"""
Main entry point for Telegram Job Fetcher
"""
import asyncio
import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.telegram_client import TelegramJobFetcher
from src.utils.logger import get_logger
from config.settings import RUNTIME

logger = get_logger('main')

async def main():
    """Main execution function"""
    try:
        logger.info("="*60)
        logger.info("Telegram Job Fetcher - Starting")
        logger.info("="*60)
        
        # Initialize fetcher
        fetcher = TelegramJobFetcher()
        
        # Initialize clients
        logger.info("Initializing Telegram clients...")
        await fetcher.initialize_clients()
        
        if not fetcher.clients:
            logger.error("No clients initialized. Exiting...")
            return
        
        # Check if user wants to authorize accounts
        if len(sys.argv) > 1 and sys.argv[1] == '--auth':
            logger.info("Authorization mode. Please complete authorization for each account.")
            logger.info("After authorization, restart without --auth flag")
            return
        
        # Start continuous fetching
        duration_days = RUNTIME.get('total_days', 30)
        logger.info(f"Starting continuous fetching for {duration_days} days...")
        
        await fetcher.run_continuous(duration_days)
        
        logger.info("Fetching completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down...")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    
    finally:
        # Cleanup
        if 'fetcher' in locals():
            await fetcher.close_clients()
        
        logger.info("="*60)
        logger.info("Telegram Job Fetcher - Stopped")
        logger.info("="*60)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())

