"""
Track auto-applied jobs in database
"""
import sqlite3
import os
import sys
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import PATHS, DATABASE
from src.utils.logger import get_logger

logger = get_logger('application_tracker')


class ApplicationTracker:
    """Track applied jobs in database"""
    
    def __init__(self):
        self.db_path = os.path.join(PATHS['database'], DATABASE['name'])
        self.create_table()
    
    def create_table(self):
        """Create applications tracking table"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                job_title TEXT,
                company_name TEXT,
                group_name TEXT,
                application_type TEXT,
                application_link TEXT,
                applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                response_date TIMESTAMP,
                match_score REAL,
                notes TEXT,
                UNIQUE(message_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Applications tracking table ready")
    
    def is_already_applied(self, message_id: str) -> bool:
        """Check if already applied to this job"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM applications WHERE message_id = ?', (message_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result is not None
    
    def record_application(self, job_info: Dict, status: str = 'sent') -> bool:
        """Record application in database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract job title from first line
            job_title = job_info['message_text'].split('\n')[0].strip('*#-_').strip()[:200]
            
            cursor.execute('''
                INSERT OR REPLACE INTO applications 
                (message_id, job_title, company_name, group_name, application_type, 
                 application_link, status, match_score, applied_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_info['message_id'],
                job_title,
                job_info.get('company_name', 'Unknown'),
                job_info.get('group_name', ''),
                job_info.get('application_type', ''),
                job_info.get('application_link', ''),
                status,
                job_info.get('match_score', 0.0),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded application for job: {job_info.get('message_id', 'unknown')}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to record application: {e}")
            return False
    
    def get_applied_jobs(self, days: int = 30) -> List[Dict]:
        """Get list of applied jobs"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM applications
            WHERE applied_date >= date('now', '-{} days')
            ORDER BY applied_date DESC
        '''.format(days))
        
        rows = cursor.fetchall()
        
        applications = [dict(row) for row in rows]
        
        conn.close()
        
        return applications
    
    def get_stats(self) -> Dict:
        """Get application statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total applications
        cursor.execute('SELECT COUNT(*) FROM applications')
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute('SELECT status, COUNT(*) FROM applications GROUP BY status')
        by_status = dict(cursor.fetchall())
        
        # By type
        cursor.execute('SELECT application_type, COUNT(*) FROM applications GROUP BY application_type')
        by_type = dict(cursor.fetchall())
        
        # Applications today
        cursor.execute('SELECT COUNT(*) FROM applications WHERE DATE(applied_date) = DATE("now")')
        today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'today': today,
            'by_status': by_status,
            'by_type': by_type
        }

