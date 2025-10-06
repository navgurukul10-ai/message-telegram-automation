"""
Message classifier to categorize job types
"""
import re
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import JOB_KEYWORDS
from src.utils.logger import get_logger

logger = get_logger('classifier')

class MessageClassifier:
    """Classify messages into tech, non-tech, and freelance jobs"""
    
    def __init__(self):
        self.tech_keywords = [kw.lower() for kw in JOB_KEYWORDS['tech']]
        self.non_tech_keywords = [kw.lower() for kw in JOB_KEYWORDS['non_tech']]
        self.freelance_keywords = [kw.lower() for kw in JOB_KEYWORDS['freelance']]
    
    def classify(self, message_text):
        """
        Classify a message and return job type and found keywords
        
        Returns:
            tuple: (job_type, keywords_found)
        """
        if not message_text or not isinstance(message_text, str):
            return None, []
        
        # Convert to lowercase for matching
        text_lower = message_text.lower()
        
        # Check if it's a job posting
        job_indicators = ['hiring', 'job', 'position', 'vacancy', 'opening', 
                         'opportunity', 'recruit', 'career', 'apply', 'join our team']
        
        has_job_indicator = any(indicator in text_lower for indicator in job_indicators)
        
        if not has_job_indicator:
            return None, []
        
        # Find matching keywords
        tech_matches = self._find_keywords(text_lower, self.tech_keywords)
        non_tech_matches = self._find_keywords(text_lower, self.non_tech_keywords)
        freelance_matches = self._find_keywords(text_lower, self.freelance_keywords)
        
        # Determine job type (priority: freelance > tech > non-tech)
        all_matches = []
        job_type = None
        
        if freelance_matches:
            job_type = 'freelance'
            all_matches.extend(freelance_matches)
        
        if tech_matches:
            if job_type == 'freelance':
                job_type = 'freelance_tech'
            else:
                job_type = 'tech'
            all_matches.extend(tech_matches)
        
        if non_tech_matches and not tech_matches:
            if job_type == 'freelance':
                job_type = 'freelance_non_tech'
            else:
                job_type = 'non_tech'
            all_matches.extend(non_tech_matches)
        
        # Remove duplicates
        all_matches = list(set(all_matches))
        
        logger.debug(f"Classified as {job_type} with keywords: {all_matches}")
        return job_type, all_matches
    
    def _find_keywords(self, text, keywords):
        """Find matching keywords in text"""
        found = []
        for keyword in keywords:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found.append(keyword)
        return found
    
    def is_job_message(self, message_text):
        """Check if message is likely a job posting"""
        if not message_text:
            return False
        
        text_lower = message_text.lower()
        
        # Job indicators
        job_indicators = [
            'hiring', 'job', 'position', 'vacancy', 'opening', 
            'opportunity', 'recruit', 'career', 'apply', 'join our team',
            'looking for', 'we are hiring', 'job opening', 'immediate opening',
            'work from home', 'wfh', 'remote', 'full-time', 'part-time',
            'experience', 'salary', 'ctc', 'package', 'interview'
        ]
        
        # Check for job indicators
        indicator_count = sum(1 for indicator in job_indicators if indicator in text_lower)
        
        # Check for contact information
        has_contact = bool(re.search(r'(\+?\d{10,13}|email|apply|contact|@)', text_lower))
        
        # Check message length (job postings are usually detailed)
        is_long_enough = len(message_text.split()) > 10
        
        return indicator_count >= 2 and (has_contact or is_long_enough)

