"""
CSV export handler for messages and groups
"""
import csv
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import PATHS, CSV_COLUMNS
from src.utils.logger import get_logger

logger = get_logger('csv_handler')

class CSVHandler:
    """Handle CSV exports for messages and groups"""
    
    def __init__(self):
        # Create CSV directory
        os.makedirs(PATHS['csv'], exist_ok=True)
        
        # Initialize CSV files
        self.messages_file = os.path.join(PATHS['csv'], 'all_messages.csv')
        self.tech_jobs_file = os.path.join(PATHS['csv'], 'tech_jobs.csv')
        self.non_tech_jobs_file = os.path.join(PATHS['csv'], 'non_tech_jobs.csv')
        self.freelance_jobs_file = os.path.join(PATHS['csv'], 'freelance_jobs.csv')
        self.groups_file = os.path.join(PATHS['csv'], 'joined_groups.csv')
        
        # Create headers if files don't exist
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Create CSV files with headers if they don't exist"""
        # Messages files
        for file_path in [self.messages_file, self.tech_jobs_file, 
                          self.non_tech_jobs_file, self.freelance_jobs_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS['messages'])
                    writer.writeheader()
                logger.info(f"Created CSV file: {file_path}")
        
        # Groups file
        if not os.path.exists(self.groups_file):
            with open(self.groups_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS['groups'])
                writer.writeheader()
            logger.info(f"Created CSV file: {self.groups_file}")
    
    def write_message(self, message_data):
        """Write message to appropriate CSV files"""
        try:
            # Write to all messages file
            self._append_to_csv(self.messages_file, message_data, CSV_COLUMNS['messages'])
            
            # Write to category-specific file
            job_type = message_data.get('job_type', '').lower()
            
            if 'tech' in job_type:
                self._append_to_csv(self.tech_jobs_file, message_data, CSV_COLUMNS['messages'])
            
            if 'non_tech' in job_type or (job_type == 'non_tech'):
                self._append_to_csv(self.non_tech_jobs_file, message_data, CSV_COLUMNS['messages'])
            
            if 'freelance' in job_type:
                self._append_to_csv(self.freelance_jobs_file, message_data, CSV_COLUMNS['messages'])
            
            logger.debug(f"Message written to CSV: {message_data['message_id']}")
            return True
        except Exception as e:
            logger.error(f"Error writing message to CSV: {e}")
            return False
    
    def write_group(self, group_data):
        """Write group information to CSV"""
        try:
            self._append_to_csv(self.groups_file, group_data, CSV_COLUMNS['groups'])
            logger.debug(f"Group written to CSV: {group_data['group_name']}")
            return True
        except Exception as e:
            logger.error(f"Error writing group to CSV: {e}")
            return False
    
    def _append_to_csv(self, file_path, data, columns):
        """Append data to CSV file"""
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            
            # Filter data to only include columns defined in the schema
            filtered_data = {k: v for k, v in data.items() if k in columns}
            
            # Fill missing columns with empty strings
            for col in columns:
                if col not in filtered_data:
                    filtered_data[col] = ''
            
            writer.writerow(filtered_data)
    
    def export_daily_summary(self, date, stats):
        """Export daily summary to CSV"""
        try:
            summary_file = os.path.join(PATHS['csv'], f'daily_summary_{date}.csv')
            
            with open(summary_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                for key, value in stats.items():
                    writer.writerow([key, value])
            
            logger.info(f"Daily summary exported: {summary_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting daily summary: {e}")
            return False

