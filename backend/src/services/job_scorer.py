"""
Job Quality Scorer - Scores jobs based on completeness and quality
"""
import re

class JobQualityScorer:
    """Score jobs based on presence of important information"""
    
    def __init__(self):
        # Common company patterns
        self.company_patterns = [
            r'\b(company|organization|firm|startup|corp|inc|ltd|pvt|limited)\b',
            r'\b([A-Z][a-z]+\s+(?:Technologies|Solutions|Systems|Software|Labs|Studios|Digital|Group|Services))\b',
            r'(?:^|\n)([A-Z][A-Z\s&]+(?:Technologies|Solutions|Systems|Software|Labs|Studios|Digital|Group|Services))',
        ]
        
        # Salary patterns
        self.salary_patterns = [
            r'\b\d+[\s-]*(?:lpa|lakh|lakhs|k|thousand)\b',
            r'(?:₹|rs\.?|inr)\s*\d+',
            r'\$\s*\d+',
            r'\b(?:salary|ctc|package|stipend)[\s:]*(?:₹|rs\.?|inr|\$)?\s*\d+',
            r'\b\d+[\s-]*(?:to|-)[\s-]*\d+[\s-]*(?:lpa|lakh|lakhs|k)\b',
        ]
        
        # Location patterns
        self.location_patterns = [
            r'\b(bangalore|bengaluru|mumbai|delhi|ncr|pune|hyderabad|chennai|kolkata|ahmedabad|gurgaon|gurugram|noida|jaipur|lucknow|chandigarh|kochi|thiruvananthapuram|indore|bhopal|nagpur|surat|vadodara|rajkot)\b',
            r'\b(india|usa|uk|singapore|dubai|uae|canada|australia|germany|netherlands|europe)\b',
            r'(?:location|based in|office in)[\s:]*([a-z\s,]+)',
        ]
        
        # Remote/WFH patterns
        self.remote_patterns = [
            r'\b(remote|wfh|work from home|work-from-home|hybrid)\b',
        ]
        
        # Skills patterns (technical and non-technical)
        self.skill_patterns = [
            r'\b(python|java|javascript|react|node|angular|vue|django|flask|spring|aws|azure|gcp|docker|kubernetes|sql|mongodb|postgresql|mysql|redis|kafka|spark|hadoop)\b',
            r'\b(html|css|typescript|golang|rust|ruby|php|swift|kotlin|scala|c\+\+|\.net|laravel)\b',
            r'\b(communication|leadership|management|sales|marketing|design|content|seo|digital marketing|social media|customer service|hr|finance|accounting|operations)\b',
            r'(?:skills?|technologies?|experience in|proficiency in)[\s:]*([a-z,\s&/]+)',
        ]
        
        # Apply link patterns (URLs only, not emails)
        self.apply_link_patterns = [
            r'(https?://\S+)',
            r'(www\.\S+\.[a-z]{2,})',
        ]
        
        # Countries outside India
        self.international_locations = [
            'usa', 'uk', 'singapore', 'dubai', 'uae', 'canada', 'australia', 
            'germany', 'netherlands', 'europe', 'united states', 'united kingdom',
            'new york', 'london', 'san francisco', 'toronto', 'sydney', 'melbourne',
            'algeria', 'algiers', 'france', 'spain', 'italy', 'japan', 'china',
            'brazil', 'mexico', 'south africa', 'egypt', 'turkey', 'russia', 'poland',
            'sweden', 'norway', 'denmark', 'finland', 'belgium', 'switzerland',
            'austria', 'ireland', 'portugal', 'greece', 'czech', 'hungary', 'romania',
            'bulgaria', 'croatia', 'slovenia', 'slovakia', 'estonia', 'latvia',
            'lithuania', 'malta', 'cyprus', 'luxembourg', 'iceland', 'new zealand',
            'south korea', 'thailand', 'vietnam', 'philippines', 'indonesia',
            'malaysia', 'taiwan', 'hong kong', 'israel', 'saudi arabia', 'qatar',
            'kuwait', 'bahrain', 'oman', 'jordan', 'lebanon', 'argentina', 'chile',
            'colombia', 'peru', 'venezuela', 'uruguay', 'paraguay', 'bolivia',
            'ecuador', 'guyana', 'suriname', 'trinidad', 'jamaica', 'cuba',
            'dominican republic', 'haiti', 'panama', 'costa rica', 'guatemala',
            'honduras', 'nicaragua', 'el salvador', 'belize', 'bahamas', 'barbados',
            'antigua', 'grenada', 'st. lucia', 'st. vincent', 'dominica', 'st. kitts',
            'nevis', 'montserrat', 'anguilla', 'british virgin islands',
            'us virgin islands', 'puerto rico', 'cayman islands', 'bermuda',
            'turks and caicos', 'aruba', 'curacao', 'bonaire', 'sint maarten',
            'saba', 'sint eustatius', 'greenland', 'faroe islands'
        ]
    
    def score_job(self, message_text):
        """
        Score a job posting based on completeness
        
        Returns:
            dict: {
                'total_score': int (0-100),
                'has_company': bool,
                'has_salary': bool,
                'has_location': bool,
                'has_skills': bool,
                'has_apply_link': bool,
                'has_remote': bool,
                'is_international': bool,
                'company_name': str or None,
                'salary_info': str or None,
                'location_info': str or None,
                'skills_info': str or None,
                'apply_link': str or None,
            }
        """
        if not message_text:
            return self._empty_score()
        
        text_lower = message_text.lower()
        
        score = 0
        result = {
            'total_score': 0,
            'has_company': False,
            'has_salary': False,
            'has_location': False,
            'has_skills': False,
            'has_apply_link': False,
            'has_remote': False,
            'is_international': False,
            'company_name': None,
            'salary_info': None,
            'location_info': None,
            'skills_info': None,
            'apply_link': None,
        }
        
        # Check for company name (20 points)
        company_match = self._find_first_match(message_text, self.company_patterns)
        if company_match:
            result['has_company'] = True
            result['company_name'] = company_match.strip()
            score += 20
        
        # Check for salary (20 points)
        salary_match = self._find_first_match(text_lower, self.salary_patterns)
        if salary_match:
            result['has_salary'] = True
            result['salary_info'] = salary_match.strip()
            score += 20
        
        # Check for apply link - URL only, not email (20 points)
        apply_link = self._find_first_match(message_text, self.apply_link_patterns)
        if apply_link and not re.search(r'@', apply_link):
            result['has_apply_link'] = True
            result['apply_link'] = apply_link.strip()
            score += 20
        
        # Check for location (15 points)
        location_match = self._find_first_match(text_lower, self.location_patterns)
        if location_match:
            result['has_location'] = True
            result['location_info'] = location_match.strip()
            score += 15
            
            # Check if international
            result['is_international'] = any(
                loc in text_lower for loc in self.international_locations
            )
        
        # Check for skills (15 points)
        skills_match = self._find_first_match(text_lower, self.skill_patterns)
        if skills_match:
            result['has_skills'] = True
            result['skills_info'] = skills_match.strip()
            score += 15
        
        # Check for remote/WFH (10 points)
        remote_match = self._find_first_match(text_lower, self.remote_patterns)
        if remote_match:
            result['has_remote'] = True
            score += 10
        
        # For international jobs, remote is MANDATORY - disqualify if not remote
        if result['is_international'] and not result['has_remote']:
            # International non-remote jobs are NOT Best Jobs - set score to 0
            score = 0
        
        result['total_score'] = score
        return result
    
    def _find_first_match(self, text, patterns):
        """Find first matching pattern in text"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Return the matched group or full match
                return match.group(1) if match.groups() else match.group(0)
        return None
    
    def _empty_score(self):
        """Return empty score result"""
        return {
            'total_score': 0,
            'has_company': False,
            'has_salary': False,
            'has_location': False,
            'has_skills': False,
            'has_apply_link': False,
            'has_remote': False,
            'is_international': False,
            'company_name': None,
            'salary_info': None,
            'location_info': None,
            'skills_info': None,
            'apply_link': None,
        }
    
    def is_best_job(self, score_result):
        """Check if job qualifies as 'best job' (score >= 60)"""
        return score_result['total_score'] >= 60

