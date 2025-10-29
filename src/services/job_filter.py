"""
Filter jobs based on user profile and preferences
"""
import json
import re
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger

logger = get_logger('job_filter')


class JobFilter:
    """Filter jobs based on user profile"""
    
    def __init__(self, profile_path: str):
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        
        self.user_skills = set([skill.lower() for skill in self.profile['skills']])
        self.preferences = self.profile['preferences']
    
    def calculate_skill_match(self, job_keywords: str) -> float:
        """Calculate skill match percentage"""
        
        if not job_keywords:
            return 0.0
        
        job_skills = set([kw.strip().lower() for kw in job_keywords.split(',')])
        
        if not job_skills:
            return 0.0
        
        # Find intersection
        matching_skills = self.user_skills.intersection(job_skills)
        
        # Calculate percentage
        match_percentage = (len(matching_skills) / len(job_skills)) * 100
        
        return round(match_percentage, 2)
    
    def check_role_match(self, message_text: str) -> bool:
        """Check if job role matches preferred roles"""
        
        message_lower = message_text.lower()
        
        for role in self.preferences['roles']:
            if role.lower() in message_lower:
                return True
        
        return False
    
    def check_required_keywords(self, message_text: str) -> bool:
        """Check if message contains required keywords"""
        
        message_lower = message_text.lower()
        
        # At least 2 required keywords should be present
        matches = sum(1 for keyword in self.preferences['required_keywords'] 
                     if keyword.lower() in message_lower)
        
        return matches >= 2
    
    def check_exclude_keywords(self, message_text: str) -> bool:
        """Check if message contains excluded keywords"""
        
        message_lower = message_text.lower()
        
        for keyword in self.preferences['exclude_keywords']:
            if keyword.lower() in message_lower:
                return True
        
        return False
    
    def filter_jobs(self, jobs: List[Dict], min_match_score: float = 30.0) -> List[Dict]:
        """Filter jobs based on profile preferences"""
        
        filtered_jobs = []
        
        for job in jobs:
            # Calculate skill match
            skill_match = self.calculate_skill_match(job.get('keywords', ''))
            
            # Check role match
            role_match = self.check_role_match(job['message_text'])
            
            # Check required keywords
            has_required = self.check_required_keywords(job['message_text'])
            
            # Check exclude keywords
            has_excluded = self.check_exclude_keywords(job['message_text'])
            
            # Decision
            if has_excluded:
                logger.debug(f"Excluded job {job['message_id']} - contains excluded keywords")
                continue
            
            if not has_required:
                logger.debug(f"Skipped job {job['message_id']} - missing required keywords")
                continue
            
            if skill_match < min_match_score and not role_match:
                logger.debug(f"Skipped job {job['message_id']} - low match score: {skill_match}%")
                continue
            
            # Add match score to job
            job['match_score'] = skill_match
            job['role_match'] = role_match
            
            filtered_jobs.append(job)
        
        # Sort by match score (highest first)
        filtered_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        logger.info(f"Filtered {len(filtered_jobs)} jobs from {len(jobs)} total jobs")
        
        return filtered_jobs

