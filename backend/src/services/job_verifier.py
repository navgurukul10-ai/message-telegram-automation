"""
Job verification and company information extraction
"""
import re
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger
from config.settings import JOB_VERIFICATION, MIN_JOB_DESCRIPTION_LENGTH

logger = get_logger('job_verifier')

class JobVerifier:
    """Verify job postings and extract company information"""
    
    def __init__(self):
        # Company name patterns
        self.company_patterns = [
            r'(?:company|firm|organization|org)[\s:]+([A-Z][A-Za-z0-9\s&\.]+)',
            r'([A-Z][A-Za-z0-9\s&\.]+)(?:\s+is\s+hiring|\s+hiring|\s+looking for)',
            r'(?:join|at|@)\s+([A-Z][A-Za-z0-9\s&\.]+)',
        ]
        
        # Website patterns
        self.website_patterns = [
            r'(https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,})',
            r'(?:website|site|web)[\s:]+([a-zA-Z0-9-]+\.[a-zA-Z]{2,})',
        ]
        
        # LinkedIn patterns
        self.linkedin_patterns = [
            r'(https?://(?:www\.)?linkedin\.com/company/[a-zA-Z0-9-]+)',
            r'linkedin[\s:]+([a-zA-Z0-9-]+)',
        ]
        
        # Contact patterns
        self.contact_patterns = [
            r'(\+?\d{10,13})',  # Phone numbers
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email
            r'(?:contact|call|whatsapp)[\s:]+(\+?\d{10,13})',
        ]
        
        # Salary patterns
        self.salary_patterns = [
            r'(?:salary|ctc|package)[\s:]*₹?\s*(\d+[\d,]*)\s*(?:to|-)\s*₹?\s*(\d+[\d,]*)',
            r'₹\s*(\d+[\d,]*)\s*(?:to|-)\s*₹?\s*(\d+[\d,]*)',
            r'(\d+)\s*(?:LPA|lpa|lakh|lakhs)',
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)',
            r'(?:experience|exp)[\s:]*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)',
        ]
        
        # Skills patterns (common tech skills)
        self.skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'node.js', 'django',
            'flask', 'spring', 'sql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes',
            'git', 'html', 'css', 'typescript', 'c++', 'c#', 'golang', 'rust',
            'machine learning', 'ml', 'ai', 'data science', 'deep learning',
            'devops', 'ci/cd', 'jenkins', 'terraform', 'ansible'
        ]
        
        # Work mode keywords
        self.work_mode_keywords = {
            'remote': ['remote', 'work from home', 'wfh', 'work from anywhere'],
            'hybrid': ['hybrid', 'flexible', 'part remote'],
            'onsite': ['onsite', 'office', 'on-site', 'work from office']
        }
        
        # Location patterns
        self.location_patterns = [
            r'(?:location|based in|office in|📍)[\s:]*([a-zA-Z\s,]+)',
            r'📍\s*([a-zA-Z\s,]+)',
        ]
        
        # Indian cities
        self.indian_cities = [
            'bangalore', 'bengaluru', 'mumbai', 'delhi', 'ncr', 'pune', 'hyderabad', 
            'chennai', 'kolkata', 'ahmedabad', 'gurgaon', 'gurugram', 'noida', 
            'jaipur', 'lucknow', 'chandigarh', 'kochi', 'thiruvananthapuram', 
            'indore', 'bhopal', 'nagpur', 'surat', 'vadodara', 'rajkot', 'goa',
            'mysore', 'coimbatore', 'vishakhapatnam', 'vijayawada', 'patna', 'raipur'
        ]
        
        # International locations
        self.international_keywords = [
            'usa', 'us', 'united states', 'uk', 'united kingdom', 'singapore', 
            'dubai', 'uae', 'canada', 'australia', 'germany', 'netherlands', 
            'europe', 'london', 'new york', 'san francisco', 'toronto', 'sydney',
            'melbourne', 'france', 'spain', 'italy', 'japan', 'china', 'brazil'
        ]
        
        # Pan India keywords
        self.pan_india_keywords = [
            'pan india', 'pan-india', 'panindia', 'all india', 'anywhere in india',
            'multiple locations', 'various locations', 'india wide'
        ]
    
    def verify_and_extract(self, message_text):
        """
        Verify job and extract all information
        Returns: dict with extracted info and verification status
        """
        if not message_text or len(message_text) < MIN_JOB_DESCRIPTION_LENGTH:
            return None
        
        result = {
            'is_verified': False,
            'verification_score': 0.0,
            'company_name': '',
            'company_website': '',
            'company_linkedin': '',
            'skills_required': '',
            'salary_range': '',
            'job_location': '',
            'work_mode': '',
            'experience_required': '',
            'job_type': '',
            'application_deadline': '',
            'contact_info': ''
        }
        
        score = 0
        max_score = 100
        
        # Extract company name
        company = self._extract_company_name(message_text)
        if company:
            result['company_name'] = company
            score += 30
        
        # Extract website
        website = self._extract_website(message_text)
        if website:
            result['company_website'] = website
            score += 15
        
        # Extract LinkedIn
        linkedin = self._extract_linkedin(message_text)
        if linkedin:
            result['company_linkedin'] = linkedin
            score += 10
        
        # Extract contact info
        contact = self._extract_contact(message_text)
        if contact:
            result['contact_info'] = contact
            score += 20
        
        # Extract skills
        skills = self._extract_skills(message_text)
        if skills:
            result['skills_required'] = ','.join(skills)
            score += 10
        
        # Extract salary
        salary = self._extract_salary(message_text)
        if salary:
            result['salary_range'] = salary
            score += 5
        
        # Extract experience
        experience = self._extract_experience(message_text)
        if experience:
            result['experience_required'] = experience
            score += 5
        
        # Extract work mode
        work_mode = self._extract_work_mode(message_text)
        if work_mode:
            result['work_mode'] = work_mode
            score += 5
        
        # Extract location
        location = self._extract_location(message_text)
        if location:
            result['job_location'] = location
            score += 5
        
        # Calculate final score
        result['verification_score'] = (score / max_score) * 100
        
        # Verify based on requirements
        result['is_verified'] = self._check_verification_requirements(result)
        
        logger.debug(f"Job verification score: {result['verification_score']:.2f}%")
        return result
    
    def _extract_company_name(self, text):
        """Extract company name from text"""
        for pattern in self.company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Clean up
                company = re.sub(r'\s+', ' ', company)
                # Take first 50 chars max
                return company[:50] if len(company) > 50 else company
        return ''
    
    def _extract_website(self, text):
        """Extract company website"""
        for pattern in self.website_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ''
    
    def _extract_linkedin(self, text):
        """Extract LinkedIn profile"""
        for pattern in self.linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ''
    
    def _extract_contact(self, text):
        """Extract contact information"""
        contacts = []
        for pattern in self.contact_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            contacts.extend(matches)
        
        # Remove duplicates and join
        contacts = list(set(contacts))
        return ', '.join(contacts[:3])  # Max 3 contacts
    
    def _extract_skills(self, text):
        """Extract required skills"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Max 10 skills
    
    def _extract_salary(self, text):
        """Extract salary range"""
        for pattern in self.salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    return f"₹{match.group(1)}-{match.group(2)}"
                else:
                    return f"₹{match.group(1)} LPA"
        return ''
    
    def _extract_experience(self, text):
        """Extract experience requirements"""
        for pattern in self.experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    return f"{match.group(1)}-{match.group(2)} years"
                else:
                    return f"{match.group(1)}+ years"
        return ''
    
    def _extract_work_mode(self, text):
        """Extract work mode (Remote/Hybrid/Onsite)"""
        text_lower = text.lower()
        
        for mode, keywords in self.work_mode_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return mode.capitalize()
        return ''
    
    def _extract_location(self, text):
        """Extract job location from text"""
        text_lower = text.lower()
        
        # Check for Pan India keywords first
        for keyword in self.pan_india_keywords:
            if keyword in text_lower:
                return 'Pan India'
        
        # Check for remote keywords
        remote_keywords = ['remote', 'wfh', 'work from home', 'work-from-home', 'work from anywhere']
        if any(kw in text_lower for kw in remote_keywords):
            return 'Remote'
        
        # Try to extract location using patterns
        for pattern in self.location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up location
                location = re.sub(r'\s+', ' ', location)
                # Take first 100 chars max
                location = location[:100] if len(location) > 100 else location
                
                # Check if it's international
                location_lower = location.lower()
                if any(kw in location_lower for kw in self.international_keywords):
                    return 'International'
                
                # If location contains "india" or "indian", it's Pan India (regardless of city)
                if 'india' in location_lower or 'indian' in location_lower:
                    return 'Pan India'
                
                # If it's a specific Indian city, it's also Pan India
                if any(city in location_lower for city in self.indian_cities):
                    return 'Pan India'
                
                return location
        
        # Fallback: check if text mentions international locations
        if any(kw in text_lower for kw in self.international_keywords):
            return 'International'
        
        return ''
    
    def _check_verification_requirements(self, result):
        """Check if job meets verification requirements"""
        requirements_met = 0
        total_requirements = 0
        
        if JOB_VERIFICATION.get('require_company_name'):
            total_requirements += 1
            if result['company_name']:
                requirements_met += 1
        
        if JOB_VERIFICATION.get('require_contact'):
            total_requirements += 1
            if result['contact_info']:
                requirements_met += 1
        
        if JOB_VERIFICATION.get('require_skills'):
            total_requirements += 1
            if result['skills_required']:
                requirements_met += 1
        
        # Must meet at least 50% of requirements
        if total_requirements == 0:
            return True
        
        return (requirements_met / total_requirements) >= 0.5

