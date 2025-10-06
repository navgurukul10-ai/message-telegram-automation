"""
Database handler for storing messages and group data
"""
import sqlite3
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import DATABASE, PATHS
from src.utils.logger import get_logger

logger = get_logger('database')

class DatabaseHandler:
    """SQLite database handler for job messages"""
    
    def __init__(self):
        # Create database directory
        os.makedirs(PATHS['database'], exist_ok=True)
        self.db_path = os.path.join(PATHS['database'], DATABASE['name'])
        self.connection = None
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return self.connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Create necessary tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Base fields for all job tables
        job_table_schema = '''(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE NOT NULL,
            group_name TEXT NOT NULL,
            group_link TEXT,
            sender TEXT,
            date TIMESTAMP,
            message_text TEXT,
            keywords_found TEXT,
            account_used TEXT,
            
            -- Enhanced Company Information
            company_name TEXT,
            company_website TEXT,
            company_linkedin TEXT,
            
            -- Job Details
            skills_required TEXT,
            salary_range TEXT,
            job_location TEXT,
            work_mode TEXT,
            experience_required TEXT,
            job_type TEXT,
            application_deadline TEXT,
            contact_info TEXT,
            
            -- Verification
            is_verified BOOLEAN DEFAULT 0,
            verification_score REAL DEFAULT 0.0,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
        
        # Tech Jobs Table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS tech_jobs {job_table_schema}
        ''')
        
        # Non-Tech Jobs Table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS non_tech_jobs {job_table_schema}
        ''')
        
        # Freelance Jobs Table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS freelance_jobs {job_table_schema}
        ''')
        
        # All Messages table (for backup/reference)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                group_name TEXT NOT NULL,
                group_link TEXT,
                sender TEXT,
                date TIMESTAMP,
                message_text TEXT,
                job_type TEXT,
                keywords_found TEXT,
                account_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                group_link TEXT UNIQUE NOT NULL,
                join_date TIMESTAMP,
                account_used TEXT,
                messages_fetched INTEGER DEFAULT 0,
                last_message_date TIMESTAMP,
                last_checked TIMESTAMP,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                groups_joined INTEGER DEFAULT 0,
                messages_fetched INTEGER DEFAULT 0,
                tech_jobs INTEGER DEFAULT 0,
                non_tech_jobs INTEGER DEFAULT 0,
                freelance_jobs INTEGER DEFAULT 0,
                accounts_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Account usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_name TEXT NOT NULL,
                date DATE NOT NULL,
                groups_joined INTEGER DEFAULT 0,
                messages_fetched INTEGER DEFAULT 0,
                last_action TIMESTAMP,
                UNIQUE(account_name, date)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database tables created successfully")
    
    def insert_message(self, message_data):
        """Insert a new message into appropriate table(s)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Insert into main messages table
            cursor.execute('''
                INSERT OR IGNORE INTO messages 
                (message_id, group_name, group_link, sender, date, message_text, 
                 job_type, keywords_found, account_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_data['message_id'],
                message_data['group_name'],
                message_data['group_link'],
                message_data['sender'],
                message_data['date'],
                message_data['message_text'],
                message_data['job_type'],
                message_data['keywords_found'],
                message_data['account_used']
            ))
            
            # Insert into category-specific table with enhanced fields
            self._insert_into_category_table(cursor, message_data)
            
            conn.commit()
            logger.debug(f"Message {message_data['message_id']} inserted successfully")
            return True
        except Exception as e:
            logger.error(f"Error inserting message: {e}")
            return False
        finally:
            conn.close()
    
    def _insert_into_category_table(self, cursor, message_data):
        """Insert message into appropriate category table"""
        job_type = message_data.get('job_type', '').lower()
        
        # Determine which table to use
        table_name = None
        if 'tech' in job_type:
            table_name = 'tech_jobs'
        elif 'freelance' in job_type:
            table_name = 'freelance_jobs'
        elif 'non_tech' in job_type:
            table_name = 'non_tech_jobs'
        else:
            return  # Unknown category
        
        # Prepare enhanced data
        cursor.execute(f'''
            INSERT OR IGNORE INTO {table_name}
            (message_id, group_name, group_link, sender, date, message_text,
             keywords_found, account_used,
             company_name, company_website, company_linkedin,
             skills_required, salary_range, job_location, work_mode,
             experience_required, job_type, application_deadline,
             contact_info, is_verified, verification_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message_data['message_id'],
            message_data['group_name'],
            message_data['group_link'],
            message_data['sender'],
            message_data['date'],
            message_data['message_text'],
            message_data['keywords_found'],
            message_data['account_used'],
            message_data.get('company_name', ''),
            message_data.get('company_website', ''),
            message_data.get('company_linkedin', ''),
            message_data.get('skills_required', ''),
            message_data.get('salary_range', ''),
            message_data.get('job_location', ''),
            message_data.get('work_mode', ''),
            message_data.get('experience_required', ''),
            message_data.get('job_type', ''),
            message_data.get('application_deadline', ''),
            message_data.get('contact_info', ''),
            message_data.get('is_verified', 0),
            message_data.get('verification_score', 0.0)
        ))
        
        logger.debug(f"Message inserted into {table_name}")
    
    def insert_group(self, group_data):
        """Insert or update group information"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO groups 
                (group_name, group_link, join_date, account_used, 
                 messages_fetched, last_message_date, last_checked)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                group_data['group_name'],
                group_data['group_link'],
                group_data.get('join_date', datetime.now()),
                group_data['account_used'],
                group_data.get('messages_fetched', 0),
                group_data.get('last_message_date'),
                datetime.now()
            ))
            conn.commit()
            logger.debug(f"Group {group_data['group_name']} inserted/updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error inserting group: {e}")
            return False
        finally:
            conn.close()
    
    def update_daily_stats(self, date, stats):
        """Update daily statistics"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO daily_stats 
                (date, groups_joined, messages_fetched, tech_jobs, non_tech_jobs, 
                 freelance_jobs, accounts_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    groups_joined = groups_joined + excluded.groups_joined,
                    messages_fetched = messages_fetched + excluded.messages_fetched,
                    tech_jobs = tech_jobs + excluded.tech_jobs,
                    non_tech_jobs = non_tech_jobs + excluded.non_tech_jobs,
                    freelance_jobs = freelance_jobs + excluded.freelance_jobs,
                    accounts_used = excluded.accounts_used
            ''', (
                date,
                stats.get('groups_joined', 0),
                stats.get('messages_fetched', 0),
                stats.get('tech_jobs', 0),
                stats.get('non_tech_jobs', 0),
                stats.get('freelance_jobs', 0),
                stats.get('accounts_used', '')
            ))
            conn.commit()
            logger.debug(f"Daily stats updated for {date}")
            return True
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")
            return False
        finally:
            conn.close()
    
    def get_processed_message_ids(self):
        """Get all processed message IDs"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT message_id FROM messages')
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching processed messages: {e}")
            return []
        finally:
            conn.close()
    
    def get_joined_groups(self):
        """Get all joined groups"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT group_link, group_name, account_used FROM groups')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching joined groups: {e}")
            return []
        finally:
            conn.close()
    
    def get_account_usage_today(self, account_name):
        """Get today's usage stats for an account"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            cursor.execute('''
                SELECT groups_joined, messages_fetched 
                FROM account_usage 
                WHERE account_name = ? AND date = ?
            ''', (account_name, today))
            
            row = cursor.fetchone()
            if row:
                return {'groups_joined': row[0], 'messages_fetched': row[1]}
            return {'groups_joined': 0, 'messages_fetched': 0}
        except Exception as e:
            logger.error(f"Error fetching account usage: {e}")
            return {'groups_joined': 0, 'messages_fetched': 0}
        finally:
            conn.close()
    
    def update_account_usage(self, account_name, groups_joined=0, messages_fetched=0):
        """Update account usage statistics"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            cursor.execute('''
                INSERT INTO account_usage 
                (account_name, date, groups_joined, messages_fetched, last_action)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(account_name, date) DO UPDATE SET
                    groups_joined = groups_joined + excluded.groups_joined,
                    messages_fetched = messages_fetched + excluded.messages_fetched,
                    last_action = excluded.last_action
            ''', (account_name, today, groups_joined, messages_fetched, datetime.now()))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating account usage: {e}")
            return False
        finally:
            conn.close()

