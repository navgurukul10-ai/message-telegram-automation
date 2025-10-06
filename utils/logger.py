"""
Logging utility for the Telegram automation system
"""
import logging
import os
from datetime import datetime
from config import LOGGING, PATHS

class Logger:
    """Custom logger with file and console output"""
    
    def __init__(self, name, log_file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOGGING['level']))
        
        # Create logs directory if it doesn't exist
        os.makedirs(PATHS['logs'], exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            LOGGING['format'],
            datefmt=LOGGING['date_format']
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file is None:
            log_file = f"{PATHS['logs']}{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)

def get_logger(name):
    """Factory function to get logger instance"""
    return Logger(name)

