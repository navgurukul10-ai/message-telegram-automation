"""
Main Configuration Settings
Import करने के लिए: from config.settings import *
"""
import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import account configuration (if exists, else use template)
try:
    from config.config import ACCOUNTS
except ImportError:
    print("⚠️  config/config.py not found. Using template.")
    print("   Copy config/config_template.py to config/config.py")
    print("   and fill in your credentials!")
    ACCOUNTS = []

# Safety Settings (IMPORTANT to avoid bans)
RATE_LIMITS = {
    'join_group_delay': (1800, 3600),
    'message_fetch_delay': (2, 5),
    'max_groups_per_day': 2,
    'max_groups_per_hour': 1,
    'daily_message_limit': 75,
    'request_delay': (5, 15),
    'working_hours': (9, 23),
}

# Filter Settings
MESSAGE_YEAR_FILTER = 2025
MIN_JOB_DESCRIPTION_LENGTH = 50

# Job Verification
JOB_VERIFICATION = {
    'require_company_name': True,
    'require_skills': False,
    'require_contact': True,
    'min_description_length': 50,
    'verify_company_website': False,
    'verify_linkedin': False
}

# Company Info Fields
COMPANY_INFO_FIELDS = [
    'company_name', 'company_website', 'company_linkedin',
    'skills_required', 'salary_range', 'job_location',
    'work_mode', 'experience_required', 'job_type',
    'application_deadline', 'contact_info'
]

# Database Configuration
DATABASE = {
    'name': 'telegram_jobs.db',
    'path': os.path.join(PROJECT_ROOT, 'data/database/')
}

# File Paths
PATHS = {
    'data': os.path.join(PROJECT_ROOT, 'data/'),
    'logs': os.path.join(PROJECT_ROOT, 'logs/'),
    'csv': os.path.join(PROJECT_ROOT, 'data/csv/'),
    'json': os.path.join(PROJECT_ROOT, 'data/json/'),
    'database': os.path.join(PROJECT_ROOT, 'data/database/'),
    'sessions': os.path.join(PROJECT_ROOT, 'sessions/'),
    'groups_json': os.path.join(PROJECT_ROOT, 'data.json')
}

# Job Keywords
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
    ],
    'fresher': [
        'fresher', 'fresh graduate', 'entry level', 'junior', 'trainee', 'intern',
        'internship', 'graduate trainee', 'fresher developer', 'fresher engineer',
        'new graduate', 'campus placement', 'campus hiring', 'college graduate',
        '0-1 year', '0-2 years', 'no experience', 'beginner', 'starter position',
        'trainee developer', 'junior developer', 'associate', 'apprentice'
    ]
}

# Logging
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# CSV Columns
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
    'check_interval': 3600,
    'total_days': 30,
    'startup_delay': (5, 15)
}

