"""
Configuration Template File
Copy this to config.py and fill in your actual credentials
"""

# Telegram Accounts Configuration
# ⚠️ NEVER commit config.py with real credentials to GitHub!
ACCOUNTS = [
    {
        'name': 'Account 1',
        'phone': '+91XXXXXXXXXX',  # Your phone number
        'api_id': 12345678,  # Your API ID from https://my.telegram.org
        'api_hash': 'your_api_hash_here',  # Your API hash
        'session_name': 'session_account1'
    },
    {
        'name': 'Account 2',
        'phone': '+91XXXXXXXXXX',
        'api_id': 12345678,
        'api_hash': 'your_api_hash_here',
        'session_name': 'session_account2'
    },
    {
        'name': 'Account 3',
        'phone': '+91XXXXXXXXXX',
        'api_id': 12345678,
        'api_hash': 'your_api_hash_here',
        'session_name': 'session_account3'
    },
    {
        'name': 'Account 4',
        'phone': '+91XXXXXXXXXX',
        'api_id': 12345678,
        'api_hash': 'your_api_hash_here',
        'session_name': 'session_account4'
    }
]

# Safety Settings (IMPORTANT to avoid bans)
# ⚠️ CRITICAL: These limits are MAXIMUM safe values to avoid account bans
RATE_LIMITS = {
    'join_group_delay': (1800, 3600),  # 30-60 minutes between joins (HUMAN-LIKE!)
    'message_fetch_delay': (2, 5),  # 2-5 seconds between message fetches
    'max_groups_per_day': 2,  # Maximum 2-3 groups per day per account (SAFE!)
    'max_groups_per_hour': 1,  # Maximum 1 group per hour
    'daily_message_limit': 75,  # Maximum 75 messages per group
    'request_delay': (5, 15),  # 5-15 seconds general delay
    'working_hours': (10, 20),  # Only work between 10 AM - 8 PM (human hours)
}

# Filter Settings
MESSAGE_YEAR_FILTER = 2025  # Only fetch messages from this year
MIN_JOB_DESCRIPTION_LENGTH = 50  # Minimum characters for valid job post

# Job Verification Settings
JOB_VERIFICATION = {
    'require_company_name': True,
    'require_skills': False,  # Optional
    'require_contact': True,
    'min_description_length': 50,
    'verify_company_website': False,  # Set True for strict verification
    'verify_linkedin': False  # Set True for strict verification
}

# Company Info Extraction
COMPANY_INFO_FIELDS = [
    'company_name',
    'company_website',
    'company_linkedin',
    'skills_required',
    'salary_range',
    'job_location',
    'work_mode',  # Remote/Hybrid/Onsite
    'experience_required',
    'job_type',  # Full-time/Part-time/Contract
    'application_deadline',
    'contact_info'
]

# Database Configuration
DATABASE = {
    'name': 'telegram_jobs.db',
    'path': './data/database/'
}

# File Paths
PATHS = {
    'data': './data/',
    'logs': './logs/',
    'csv': './data/csv/',
    'json': './data/json/',
    'database': './data/database/',
    'sessions': './sessions/',
    'groups_json': './data.json'
}

# Job Classification Keywords
JOB_KEYWORDS = {
    'tech': [
        'python', 'java', 'javascript', 'developer', 'programmer', 'software',
        'engineer', 'full stack', 'frontend', 'backend', 'devops', 'data scientist',
        'machine learning', 'ai', 'ml', 'react', 'angular', 'node.js', 'django',
        'flask', 'api', 'database', 'sql', 'mongodb', 'aws', 'cloud', 'docker',
        'kubernetes', 'git', 'coding', 'html', 'css', 'mobile app', 'android',
        'ios', 'swift', 'kotlin', 'flutter', 'react native', 'web development',
        'software development', 'qa', 'testing', 'automation', 'selenium', 
        'cybersecurity', 'blockchain', 'smart contract', 'solidity', 'web3',
        'ui/ux', 'designer', 'figma', 'adobe', 'tech lead', 'architect'
    ],
    'non_tech': [
        'marketing', 'sales', 'hr', 'human resource', 'accountant', 'finance',
        'manager', 'business analyst', 'content writer', 'copywriter', 'seo',
        'digital marketing', 'social media', 'customer service', 'support',
        'administration', 'executive', 'operations', 'logistics', 'procurement',
        'legal', 'lawyer', 'consultant', 'project manager', 'product manager',
        'business development', 'designer', 'graphic design', 'video editor'
    ],
    'freelance': [
        'freelance', 'freelancer', 'gig', 'contract', 'part-time', 'part time',
        'remote work', 'work from home', 'wfh', 'upwork', 'fiverr', 'toptal',
        'consultant', 'hourly', 'project basis', 'flexible hours', 'independent'
    ]
}

# Logging Configuration
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Tracking Files
TRACKING_FILES = {
    'joined_groups': './data/json/joined_groups.json',
    'processed_messages': './data/json/processed_messages.json',
    'daily_stats': './data/json/daily_stats.json'
}

# CSV Export Settings
CSV_COLUMNS = {
    'messages': [
        'message_id', 'group_name', 'group_link', 'sender', 'date', 
        'message_text', 'job_type', 'keywords_found', 'account_used'
    ],
    'groups': [
        'group_name', 'group_link', 'join_date', 'account_used', 
        'messages_fetched', 'last_message_date'
    ]
}

# Runtime Settings
RUNTIME = {
    'check_interval': 3600,  # Check for new messages every hour (in seconds)
    'total_days': 30,  # Run for 30 days
    'startup_delay': (5, 15)  # Random delay on startup
}

