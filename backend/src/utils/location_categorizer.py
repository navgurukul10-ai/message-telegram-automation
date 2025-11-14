"""
Location categorization utility
Categorizes job locations into: Pan India, Remote, International, or specific city
"""
import re

class LocationCategorizer:
    """Categorize job locations"""
    
    def __init__(self):
        # Pan India keywords
        self.pan_india_keywords = [
            'pan india', 'pan-india', 'panindia', 'all india', 'anywhere in india',
            'multiple locations', 'various locations', 'india wide', 'any location in india'
        ]
        
        # Remote keywords
        self.remote_keywords = [
            'remote', 'wfh', 'work from home', 'work-from-home', 'work from anywhere',
            'work remotely', 'remote work', 'fully remote'
        ]
        
        # International locations
        self.international_keywords = [
            'usa', 'us', 'united states', 'uk', 'united kingdom', 'singapore', 
            'dubai', 'uae', 'canada', 'australia', 'germany', 'netherlands', 
            'europe', 'london', 'new york', 'san francisco', 'toronto', 'sydney',
            'melbourne', 'france', 'spain', 'italy', 'japan', 'china', 'brazil',
            'mexico', 'south africa', 'egypt', 'turkey', 'russia', 'poland',
            'sweden', 'norway', 'denmark', 'finland', 'belgium', 'switzerland',
            'austria', 'ireland', 'portugal', 'greece', 'new zealand', 'south korea'
        ]
        
        # Indian cities
        self.indian_cities = [
            'bangalore', 'bengaluru', 'mumbai', 'delhi', 'ncr', 'pune', 'hyderabad', 
            'chennai', 'kolkata', 'ahmedabad', 'gurgaon', 'gurugram', 'noida', 
            'jaipur', 'lucknow', 'chandigarh', 'kochi', 'thiruvananthapuram', 
            'indore', 'bhopal', 'nagpur', 'surat', 'vadodara', 'rajkot', 'goa',
            'mysore', 'coimbatore', 'vishakhapatnam', 'vijayawada', 'patna', 'raipur'
        ]
    
    def categorize(self, location_text, message_text=None):
        """
        Categorize location into: Pan India, Remote, International, or return as-is
        
        Args:
            location_text: The location string from job_location field
            message_text: Optional full message text for additional context
        
        Returns:
            str: 'Pan India', 'Remote', 'International', or the original location
        """
        if not location_text:
            # If no location, check message text for remote keywords
            if message_text:
                text_lower = message_text.lower()
                if any(kw in text_lower for kw in self.remote_keywords):
                    return 'Remote'
            return ''
        
        location_lower = location_text.lower().strip()
        
        # Check for Pan India keywords
        for keyword in self.pan_india_keywords:
            if keyword in location_lower:
                return 'Pan India'
        
        # Check for Remote keywords
        for keyword in self.remote_keywords:
            if keyword in location_lower:
                return 'Remote'
        
        # Check for International keywords
        for keyword in self.international_keywords:
            if keyword in location_lower:
                return 'International'
        
        # If location contains "india" or "indian", it's Pan India (regardless of city)
        if 'india' in location_lower or 'indian' in location_lower:
            return 'Pan India'
        
        # If it's a specific Indian city, it's also Pan India
        if any(city in location_lower for city in self.indian_cities):
            return 'Pan India'
        
        # If message text contains "india" or Indian cities but location is empty, it's Pan India
        if message_text and not location_text:
            msg_lower = message_text.lower()
            if 'india' in msg_lower or any(city in msg_lower for city in self.indian_cities):
                # Check if it's not international
                if not any(kw in msg_lower for kw in self.international_keywords):
                    return 'Pan India'
        
        # Default: return as-is (could be a specific city name from other countries)
        return location_text.strip()
    
    def get_location_category(self, location_text, message_text=None):
        """
        Get location category for filtering
        
        Returns:
            str: 'pan_india', 'remote', 'international', or 'specific_city'
        """
        categorized = self.categorize(location_text, message_text)
        
        if categorized == 'Pan India':
            return 'pan_india'
        elif categorized == 'Remote':
            return 'remote'
        elif categorized == 'International':
            return 'international'
        else:
            return 'specific_city'

