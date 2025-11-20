"""
Extract and categorize job application links from messages
"""
import re
import sqlite3
from typing import List, Dict, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import PATHS, DATABASE
from src.utils.logger import get_logger

logger = get_logger('link_extractor')


class LinkExtractor:
    """Extract and categorize application links from job messages"""
    
    def __init__(self):
        self.db_path = os.path.join(PATHS['database'], DATABASE['name'])
    
    def _clean_url(self, url: str) -> str:
        """Clean URL by removing special characters from start and end"""
        if not url:
            return url
        
        # Remove special characters from start (common markdown/formatting chars)
        url = url.lstrip('*_~`[](){}|\\^<>"\'')
        
        # Remove special characters from end (punctuation and formatting)
        url = url.rstrip('*_~`[](){}|\\^<>"\'.,;:)>')
        
        return url.strip()
    
    def extract_links_from_message(self, message_text: str) -> Dict[str, any]:
        """Extract all types of application info from message"""
        
        result = {
            'urls': [],
            'emails': [],
            'application_type': 'unknown',
            'application_link': None
        }
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, message_text, re.IGNORECASE)
        result['urls'] = [self._clean_url(url) for url in urls]
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message_text)
        result['emails'] = emails
        
        # Categorize application type
        if urls:
            for url in result['urls']:
                # Clean the URL before processing
                url = self._clean_url(url)
                url_lower = url.lower()
                
                # LinkedIn
                if 'linkedin.com/jobs' in url_lower or 'linkedin.com/job' in url_lower:
                    result['application_type'] = 'linkedin'
                    result['application_link'] = url
                    break
                
                # Naukri
                elif 'naukri.com' in url_lower:
                    result['application_type'] = 'naukri'
                    result['application_link'] = url
                    break
                
                # Indeed
                elif 'indeed.com' in url_lower:
                    result['application_type'] = 'indeed'
                    result['application_link'] = url
                    break
                
                # Instahyre
                elif 'instahyre.com' in url_lower:
                    result['application_type'] = 'instahyre'
                    result['application_link'] = url
                    break
                
                # General career/job URLs
                elif any(keyword in url_lower for keyword in ['career', 'job', 'apply', 'recruitment', 'hiring']):
                    result['application_type'] = 'career_page'
                    result['application_link'] = url
                    break
        
        # If no URL found, check for email
        if result['application_type'] == 'unknown' and emails:
            result['application_type'] = 'email'
            result['application_link'] = emails[0]
        
        return result
    
    def get_applicable_jobs(self, job_type: str = 'tech', days: int = 7) -> List[Dict]:
        """Get jobs that can be auto-applied to"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query based on job type
        if job_type == 'all':
            query = """
                SELECT message_id, message_text, job_type, group_name, date, keywords_found
                FROM messages
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(days)
        else:
            query = """
                SELECT message_id, message_text, job_type, group_name, date, keywords_found
                FROM messages
                WHERE job_type LIKE '%{}%' 
                AND date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(job_type, days)
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        applicable_jobs = []
        
        for row in rows:
            link_info = self.extract_links_from_message(row['message_text'])
            
            if link_info['application_type'] != 'unknown':
                applicable_jobs.append({
                    'message_id': row['message_id'],
                    'message_text': row['message_text'],
                    'job_type': row['job_type'],
                    'group_name': row['group_name'],
                    'date': row['date'],
                    'keywords': row['keywords_found'],
                    'application_type': link_info['application_type'],
                    'application_link': link_info['application_link'],
                    'urls': link_info['urls'],
                    'emails': link_info['emails']
                })
        
        conn.close()
        
        logger.info(f"Found {len(applicable_jobs)} applicable jobs out of {len(rows)} total jobs")
        
        return applicable_jobs
    
    def categorize_by_type(self, jobs: List[Dict]) -> Dict[str, List]:
        """Categorize jobs by application type"""
        
        categorized = {
            'email': [],
            'linkedin': [],
            'naukri': [],
            'indeed': [],
            'instahyre': [],
            'career_page': [],
            'unknown': []
        }
        
        for job in jobs:
            app_type = job.get('application_type', 'unknown')
            categorized[app_type].append(job)
        
        return categorized

