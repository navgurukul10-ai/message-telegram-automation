"""
Campus Tracking and Follow-up Service
Tracks campus data submissions and manages follow-ups
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import PATHS, DATABASE
from src.utils.logger import get_logger

logger = get_logger('campus_tracker')


class CampusTracker:
    """Tracks campus data submissions and manages follow-ups"""
    
    def __init__(self):
        self.db_path = os.path.join(PATHS['database'], DATABASE['name'])
    
    def register_campus(self, campus_code: str, campus_name: str, location: str = None,
                       contact_person: str = None, contact_email: str = None,
                       contact_phone: str = None, expected_submission_date: str = None) -> Dict:
        """Register a new campus"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO campuses
                (campus_code, campus_name, location, contact_person, contact_email,
                 contact_phone, expected_submission_date, submission_status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
            ''', (
                campus_code, campus_name, location, contact_person,
                contact_email, contact_phone, expected_submission_date
            ))
            
            conn.commit()
            logger.info(f"Registered campus: {campus_name} ({campus_code})")
            
            return {
                'status': 'success',
                'message': f'Campus {campus_name} registered successfully'
            }
        except Exception as e:
            logger.error(f"Error registering campus: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            conn.close()
    
    def update_campus_submission(self, campus_identifier: str, submission_date: str = None, 
                                by_name: bool = False) -> Dict:
        """
        Update campus submission status when data is received
        
        Args:
            campus_identifier: Campus code or campus name
            submission_date: Submission date (defaults to today)
            by_name: If True, search by campus_name instead of campus_code
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            submission_date = submission_date or datetime.now().date().isoformat()
            
            # Get campus code if searching by name
            if by_name:
                cursor.execute('SELECT campus_code FROM campuses WHERE campus_name = ?', (campus_identifier,))
                result = cursor.fetchone()
                if not result:
                    return {'status': 'error', 'error': f'Campus "{campus_identifier}" not found'}
                campus_code = result[0]
            else:
                campus_code = campus_identifier
            
            # Count students for this campus
            cursor.execute('''
                SELECT COUNT(*) FROM students WHERE campus_name = 
                (SELECT campus_name FROM campuses WHERE campus_code = ?)
            ''', (campus_code,))
            student_count = cursor.fetchone()[0]
            
            # Update campus record
            cursor.execute('''
                UPDATE campuses
                SET last_submission_date = ?,
                    submission_status = 'submitted',
                    submission_count = submission_count + 1,
                    students_submitted = ?,
                    last_follow_up_date = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE campus_code = ?
            ''', (submission_date, student_count, campus_code))
            
            conn.commit()
            
            # Calculate data completeness
            self._calculate_completeness(campus_code)
            
            logger.info(f"Updated submission for campus: {campus_code}")
            
            return {
                'status': 'success',
                'students_count': student_count
            }
        except Exception as e:
            logger.error(f"Error updating campus submission: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            conn.close()
    
    def _calculate_completeness(self, campus_code: str):
        """Calculate data completeness percentage for a campus"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get total students
            cursor.execute('''
                SELECT COUNT(*) FROM students 
                WHERE campus_name = (SELECT campus_name FROM campuses WHERE campus_code = ?)
            ''', (campus_code,))
            total = cursor.fetchone()[0]
            
            if total == 0:
                completeness = 0.0
            else:
                # Count students with complete data (have skills, category, etc.)
                cursor.execute('''
                    SELECT COUNT(*) FROM students 
                    WHERE campus_name = (SELECT campus_name FROM campuses WHERE campus_code = ?)
                    AND skills IS NOT NULL AND skills != ''
                    AND category IS NOT NULL AND category != ''
                ''', (campus_code,))
                complete = cursor.fetchone()[0]
                completeness = (complete / total) * 100 if total > 0 else 0.0
            
            cursor.execute('''
                UPDATE campuses
                SET data_completeness = ?,
                    total_students = ?
                WHERE campus_code = ?
            ''', (completeness, total, campus_code))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error calculating completeness: {e}")
        finally:
            conn.close()
    
    def get_campus_status(self, campus_code: Optional[str] = None) -> List[Dict]:
        """Get status of all campuses or a specific campus"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if campus_code:
            cursor.execute('SELECT * FROM campuses WHERE campus_code = ?', (campus_code,))
        else:
            cursor.execute('SELECT * FROM campuses ORDER BY campus_name')
        
        rows = cursor.fetchall()
        campuses = [dict(row) for row in rows]
        
        # Check for overdue submissions
        today = datetime.now().date()
        for campus in campuses:
            if campus.get('expected_submission_date'):
                expected = datetime.strptime(campus['expected_submission_date'], '%Y-%m-%d').date()
                if expected < today and campus['submission_status'] != 'submitted':
                    campus['is_overdue'] = True
                    campus['days_overdue'] = (today - expected).days
                else:
                    campus['is_overdue'] = False
                    campus['days_overdue'] = 0
            else:
                campus['is_overdue'] = False
                campus['days_overdue'] = 0
        
        conn.close()
        return campuses
    
    def create_follow_up(self, campus_code: str, follow_up_type: str = 'email',
                        priority: str = 'medium', scheduled_date: str = None,
                        notes: str = None) -> Dict:
        """Create a follow-up task for a campus"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get campus name
            cursor.execute('SELECT campus_name FROM campuses WHERE campus_code = ?', (campus_code,))
            result = cursor.fetchone()
            if not result:
                return {'status': 'error', 'error': 'Campus not found'}
            
            campus_name = result[0]
            scheduled_date = scheduled_date or datetime.now().date().isoformat()
            
            cursor.execute('''
                INSERT INTO follow_ups
                (campus_id, campus_name, follow_up_type, status, priority,
                 scheduled_date, notes)
                VALUES (
                    (SELECT id FROM campuses WHERE campus_code = ?),
                    ?, ?, 'pending', ?, ?, ?
                )
            ''', (campus_code, campus_name, follow_up_type, priority, scheduled_date, notes))
            
            # Update campus last_follow_up_date
            cursor.execute('''
                UPDATE campuses
                SET last_follow_up_date = ?,
                    follow_up_count = follow_up_count + 1
                WHERE campus_code = ?
            ''', (scheduled_date, campus_code))
            
            conn.commit()
            logger.info(f"Created follow-up for campus: {campus_name}")
            
            return {
                'status': 'success',
                'message': f'Follow-up created for {campus_name}'
            }
        except Exception as e:
            logger.error(f"Error creating follow-up: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_pending_follow_ups(self) -> List[Dict]:
        """Get all pending follow-ups"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, c.campus_code, c.contact_email, c.contact_phone
            FROM follow_ups f
            JOIN campuses c ON f.campus_id = c.id
            WHERE f.status = 'pending'
            ORDER BY 
                CASE f.priority
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                f.scheduled_date
        ''')
        
        rows = cursor.fetchall()
        follow_ups = [dict(row) for row in rows]
        
        conn.close()
        return follow_ups
    
    def complete_follow_up(self, follow_up_id: int, notes: str = None) -> Dict:
        """Mark a follow-up as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE follow_ups
                SET status = 'completed',
                    completed_date = CURRENT_DATE,
                    completed_at = CURRENT_TIMESTAMP,
                    notes = COALESCE(?, notes)
                WHERE id = ?
            ''', (notes, follow_up_id))
            
            conn.commit()
            logger.info(f"Completed follow-up: {follow_up_id}")
            
            return {'status': 'success'}
        except Exception as e:
            logger.error(f"Error completing follow-up: {e}")
            return {'status': 'error', 'error': str(e)}
        finally:
            conn.close()
    
    def auto_create_follow_ups_for_overdue(self) -> Dict:
        """Automatically create follow-ups for campuses with overdue submissions"""
        campuses = self.get_campus_status()
        overdue_campuses = [c for c in campuses if c.get('is_overdue', False)]
        
        created = 0
        for campus in overdue_campuses:
            # Determine priority based on days overdue
            days_overdue = campus.get('days_overdue', 0)
            if days_overdue > 14:
                priority = 'urgent'
            elif days_overdue > 7:
                priority = 'high'
            else:
                priority = 'medium'
            
            result = self.create_follow_up(
                campus['campus_code'],
                follow_up_type='email',
                priority=priority,
                notes=f'Automatic follow-up: {days_overdue} days overdue'
            )
            
            if result['status'] == 'success':
                created += 1
        
        return {
            'status': 'success',
            'follow_ups_created': created,
            'overdue_campuses': len(overdue_campuses)
        }
    
    def get_dashboard_stats(self) -> Dict:
        """Get overall dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total campuses
            cursor.execute('SELECT COUNT(*) FROM campuses')
            total_campuses = cursor.fetchone()[0]
            
            # Campuses with submitted data
            cursor.execute("SELECT COUNT(*) FROM campuses WHERE submission_status = 'submitted'")
            submitted_campuses = cursor.fetchone()[0]
            
            # Pending campuses
            cursor.execute("SELECT COUNT(*) FROM campuses WHERE submission_status = 'pending'")
            pending_campuses = cursor.fetchone()[0]
            
            # Overdue campuses
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(*) FROM campuses
                WHERE expected_submission_date < ? AND submission_status != 'submitted'
            ''', (today.isoformat(),))
            overdue_campuses = cursor.fetchone()[0]
            
            # Total students
            cursor.execute('SELECT COUNT(*) FROM students')
            total_students = cursor.fetchone()[0]
            
            # Pending follow-ups
            cursor.execute("SELECT COUNT(*) FROM follow_ups WHERE status = 'pending'")
            pending_follow_ups = cursor.fetchone()[0]
            
            return {
                'total_campuses': total_campuses,
                'submitted_campuses': submitted_campuses,
                'pending_campuses': pending_campuses,
                'overdue_campuses': overdue_campuses,
                'total_students': total_students,
                'pending_follow_ups': pending_follow_ups,
                'submission_rate': (submitted_campuses / total_campuses * 100) if total_campuses > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
        finally:
            conn.close()

