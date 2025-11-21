"""
Data Aggregation Service
Consolidates student data from multiple sources (CSV, APIs, databases)
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import PATHS, DATABASE
from src.utils.logger import get_logger

logger = get_logger('data_aggregator')


class DataAggregator:
    """Aggregates student data from multiple sources into unified format"""
    
    def __init__(self):
        self.db_path = os.path.join(PATHS['database'], DATABASE['name'])
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json']
    
    def aggregate_from_csv(self, file_path: str, campus_name: Optional[str] = None) -> Dict:
        """
        Aggregate student data from CSV file
        
        Expected CSV columns:
        - student_id, name, email, phone, campus, resume_url, etc.
        """
        try:
            start_time = datetime.now()
            df = pd.read_csv(file_path)
            
            records_processed = len(df)
            records_added = 0
            records_updated = 0
            records_skipped = 0
            errors = []
            
            # Keep original column names for matching (Google Forms has exact names)
            df.columns = df.columns.str.strip()
            
            # Map common column name variations (including Google Forms format)
            column_mapping = {
                'student_id': ['student_id', 'id', 'studentid', 'student_code', 'timestamp', 'Timestamp'],
                'name': ['name', 'Name', 'student_name', 'full_name', 'fullname'],
                'email': ['email', 'Email', 'email_id', 'email_address'],
                'phone': ['phone', 'Phone', 'phone_number', 'mobile', 'contact'],
                'campus': ['campus', 'Campus', 'campus_name', 'center', 'location', 'Course', 'course'],
                'resume_url': [
                    'resume_url', 'resume', 'resume_link', 'cv_url', 'cv',
                    'Resume Link (Google Drive / PDF Link)', 'Resume Link (Google Drive / PD',
                    'resume link (google drive / pdf link)', 'resume link',
                    'resume_link', 'Resume Link'
                ],
                'portfolio_url': [
                    'portfolio', 'Portfolio / GitHub Link', 'portfolio / github link',
                    'github', 'portfolio_link', 'github_link', 'Portfolio'
                ],
                'technical_skills': [
                    'Technical Skills', 'technical skills', 'tech_skills', 
                    'technical_skills', 'skills'
                ],
                'non_technical_skills': [
                    'Non-Technical Skills', 'non-technical skills', 
                    'non_technical_skills', 'non tech skills'
                ],
                'tech_interests': [
                    'Tech Interests', 'tech interests', 'tech_interests', 
                    'technical interests'
                ],
                'non_tech_interests': [
                    'Non-Tech Interests', 'non-tech interests', 
                    'non_tech_interests', 'non tech interests'
                ],
                'preferred_mode': [
                    'Preferred Mode', 'preferred mode', 'preferred_mode', 
                    'work_mode', 'work mode'
                ],
                'looking_for': [
                    'Looking for', 'looking for', 'looking_for', 
                    'job_type', 'job type'
                ],
                'career_goal': [
                    'Career Goal', 'career goal', 'career_goal', 'goal'
                ],
                'educational_qualification': [
                    'Educational Qualification', 'educational qualification', 
                    'education', 'qualification', 'degree'
                ],
                'institute_name': [
                    'Institute name', 'institute name', 'institute_name', 
                    'institution', 'college', 'university'
                ],
                'status': ['status', 'Status', 'student_status', 'placement_status']
            }
            
            # Find actual column names (case-insensitive, handles spaces)
            actual_columns = {}
            for standard_name, variations in column_mapping.items():
                for col in df.columns:
                    col_normalized = str(col).strip().lower().replace(' ', '_').replace('-', '_')
                    for variation in variations:
                        var_normalized = str(variation).strip().lower().replace(' ', '_').replace('-', '_')
                        # Try exact match first
                        if col.strip() == variation.strip():
                            actual_columns[standard_name] = col
                            break
                        # Try normalized match
                        elif col_normalized == var_normalized:
                            actual_columns[standard_name] = col
                            break
                    if standard_name in actual_columns:
                        break
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for index, row in df.iterrows():
                try:
                    # Pass actual_columns mapping to normalization function
                    student_data = self._normalize_student_data(row, actual_columns, campus_name, index + 1)
                    
                    # Check for existing student using name + email or name + campus
                    existing_student_id = self._find_existing_student(cursor, student_data)
                    
                    if existing_student_id:
                        # Student exists - update with new data
                        # Preserve existing student_id
                        student_data['student_id'] = existing_student_id
                        self._update_student(cursor, student_data, existing_student_id)
                        records_updated += 1
                    else:
                        # New student - generate student_id if missing
                        if not student_data.get('student_id'):
                            import time
                            student_data['student_id'] = f"STU_{int(time.time())}_{index + 1}"
                        
                        # Insert new student
                        self._insert_student(cursor, student_data)
                        records_added += 1
                        
                except Exception as e:
                    records_skipped += 1
                    error_msg = f"Row {index + 1}: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            
            conn.commit()
            conn.close()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log aggregation
            self._log_aggregation('csv', file_path, records_processed, records_added, 
                                records_updated, records_skipped, errors, execution_time)
            
            return {
                'status': 'success',
                'records_processed': records_processed,
                'records_added': records_added,
                'records_updated': records_updated,
                'records_skipped': records_skipped,
                'errors': errors,
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Error aggregating from CSV: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def aggregate_from_excel(self, file_path: str, sheet_name: Optional[str] = None, 
                            campus_name: Optional[str] = None) -> Dict:
        """Aggregate student data from Excel file"""
        try:
            start_time = datetime.now()
            
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Use same processing as CSV
            return self._process_dataframe(df, file_path, 'excel', campus_name, start_time)
            
        except Exception as e:
            logger.error(f"Error aggregating from Excel: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def aggregate_from_json(self, file_path: str, campus_name: Optional[str] = None) -> Dict:
        """Aggregate student data from JSON file"""
        try:
            start_time = datetime.now()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to DataFrame for uniform processing
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If it's a dict with a 'students' key
                if 'students' in data:
                    df = pd.DataFrame(data['students'])
                else:
                    df = pd.DataFrame([data])
            else:
                raise ValueError("Invalid JSON structure")
            
            return self._process_dataframe(df, file_path, 'json', campus_name, start_time)
            
        except Exception as e:
            logger.error(f"Error aggregating from JSON: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _process_dataframe(self, df: pd.DataFrame, source_path: str, source_type: str,
                          campus_name: Optional[str], start_time: datetime) -> Dict:
        """Process DataFrame and insert into database"""
        records_processed = len(df)
        records_added = 0
        records_updated = 0
        records_skipped = 0
        errors = []
        
        # Keep original column names for matching (Google Forms has exact names)
        df.columns = df.columns.str.strip()
        
        # Use same column mapping as CSV (includes Google Forms format)
        column_mapping = {
            'student_id': ['student_id', 'id', 'studentid', 'student_code', 'timestamp', 'Timestamp'],
            'name': ['name', 'Name', 'student_name', 'full_name', 'fullname'],
            'email': ['email', 'Email', 'email_id', 'email_address'],
            'phone': ['phone', 'Phone', 'phone_number', 'mobile', 'contact'],
            'campus': ['campus', 'Campus', 'campus_name', 'center', 'location', 'Course', 'course'],
            'resume_url': [
                'resume_url', 'resume', 'resume_link', 'cv_url', 'cv',
                'Resume Link (Google Drive / PDF Link)', 'Resume Link (Google Drive / PD',
                'resume link (google drive / pdf link)', 'resume link',
                'resume_link', 'Resume Link'
            ],
            'portfolio_url': [
                'portfolio', 'Portfolio / GitHub Link', 'portfolio / github link',
                'github', 'portfolio_link', 'github_link', 'Portfolio'
            ],
            'technical_skills': [
                'Technical Skills', 'technical skills', 'tech_skills', 
                'technical_skills', 'skills'
            ],
            'non_technical_skills': [
                'Non-Technical Skills', 'non-technical skills', 
                'non_technical_skills', 'non tech skills'
            ],
            'preferred_mode': [
                'Preferred Mode', 'preferred mode', 'preferred_mode', 
                'work_mode', 'work mode'
            ],
            'looking_for': [
                'Looking for', 'looking for', 'looking_for', 
                'job_type', 'job type'
            ],
            'career_goal': [
                'Career Goal', 'career goal', 'career_goal', 'goal'
            ],
            'status': ['status', 'Status', 'student_status', 'placement_status']
        }
        
        # Find actual column names (case-insensitive, handles spaces)
        actual_columns = {}
        for standard_name, variations in column_mapping.items():
            for col in df.columns:
                col_normalized = str(col).strip().lower().replace(' ', '_').replace('-', '_')
                for variation in variations:
                    var_normalized = str(variation).strip().lower().replace(' ', '_').replace('-', '_')
                    # Try exact match first
                    if col.strip() == variation.strip():
                        actual_columns[standard_name] = col
                        break
                    # Try normalized match
                    elif col_normalized == var_normalized:
                        actual_columns[standard_name] = col
                        break
                if standard_name in actual_columns:
                    break
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for index, row in df.iterrows():
            try:
                student_data = self._normalize_student_data(row, actual_columns, campus_name, index + 1)
                
                # Check for existing student using name + email or name + campus
                existing_student_id = self._find_existing_student(cursor, student_data)
                
                if existing_student_id:
                    # Student exists - update with new data
                    # Preserve existing student_id
                    student_data['student_id'] = existing_student_id
                    self._update_student(cursor, student_data, existing_student_id)
                    records_updated += 1
                else:
                    # New student - generate student_id if missing
                    if not student_data.get('student_id'):
                        import time
                        student_data['student_id'] = f"STU_{int(time.time())}_{index + 1}"
                    
                    # Insert new student
                    self._insert_student(cursor, student_data)
                    records_added += 1
                
            except Exception as e:
                records_skipped += 1
                error_msg = f"Row {index + 1}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        conn.commit()
        conn.close()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        self._log_aggregation(source_type, source_path, records_processed, records_added,
                            records_updated, records_skipped, errors, execution_time)
        
        return {
            'status': 'success',
            'records_processed': records_processed,
            'records_added': records_added,
            'records_updated': records_updated,
            'records_skipped': records_skipped,
            'errors': errors,
            'execution_time': execution_time
        }
    
    def _normalize_student_data(self, row: pd.Series, actual_columns: Dict, 
                               campus_name: Optional[str], row_number: int = 0) -> Dict:
        """Normalize student data from row - all fields optional, handles Google Forms format
        
        Args:
            row: DataFrame row
            actual_columns: Dict mapping standard names to actual column names in CSV
                          e.g., {'name': 'Name', 'email': 'Email', ...}
            campus_name: Optional campus name override
            row_number: Row number for generating default names
        """
        data = {}
        
        # Extract mapped columns (all optional)
        # actual_columns is a dict like {'name': 'Name', 'email': 'Email', ...}
        for standard_name, actual_col in actual_columns.items():
            if actual_col and actual_col in row.index and pd.notna(row[actual_col]):
                value = str(row[actual_col]).strip()
                if value and value.lower() not in ['nan', 'none', 'null', '']:
                    data[standard_name] = value
        
        # Also scan all columns for any unmapped fields that might be useful
        for col in row.index:
            col_lower = str(col).strip().lower().replace(' ', '_').replace('-', '_')
            if pd.notna(row[col]):
                value = str(row[col]).strip()
                if value and value.lower() not in ['nan', 'none', 'null', '']:
                    # Auto-detect common patterns
                    if 'name' in col_lower and 'name' not in data:
                        data['name'] = value
                    elif 'email' in col_lower and 'email' not in data:
                        data['email'] = value
                    elif ('phone' in col_lower or 'mobile' in col_lower) and 'phone' not in data:
                        data['phone'] = value
                    elif ('resume' in col_lower or 'cv' in col_lower) and 'resume_url' not in data:
                        data['resume_url'] = value
                    elif 'github' in col_lower or 'portfolio' in col_lower:
                        if 'portfolio_url' not in data:
                            data['portfolio_url'] = value
        
        # Use provided campus name if available
        if campus_name:
            data['campus_name'] = campus_name
        elif 'campus_name' not in data:
            # Try to get from course or campus field
            if 'campus' in data:
                data['campus_name'] = data.get('campus')
            elif 'course' in data:
                data['campus_name'] = data.get('course')
        
        # Set defaults for required fields
        data.setdefault('status', 'active')
        data.setdefault('data_source', 'csv')
        
        # Ensure name exists (use student_id or row number as fallback)
        if 'name' not in data or not data.get('name'):
            if 'student_id' in data:
                data['name'] = data['student_id']
            else:
                data['name'] = f"Student {row_number}"
        
        # Store additional Google Forms fields in a JSON field for later use
        additional_data = {}
        for key in ['technical_skills', 'non_technical_skills', 'tech_interests', 
                   'non_tech_interests', 'preferred_mode', 'looking_for', 
                   'career_goal', 'educational_qualification', 'institute_name', 
                   'portfolio_url']:
            if key in data:
                additional_data[key] = data[key]
        
        if additional_data:
            data['additional_info'] = json.dumps(additional_data)
        
        return data
    
    def _find_existing_student(self, cursor, student_data: Dict) -> Optional[str]:
        """
        Find existing student using multiple criteria to prevent duplicates.
        Returns student_id if found, None otherwise.
        """
        name = student_data.get('name')
        email = student_data.get('email')
        campus_name = student_data.get('campus_name')
        student_id = student_data.get('student_id')
        
        if not name or name == 'Unknown':
            return None
        
        # First, check by student_id if provided
        if student_id:
            cursor.execute('SELECT student_id FROM students WHERE student_id = ?', (student_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
        
        # Check by name + email (most reliable)
        if email:
            cursor.execute('''
                SELECT student_id FROM students 
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) 
                AND LOWER(TRIM(email)) = LOWER(TRIM(?))
            ''', (name, email))
            result = cursor.fetchone()
            if result:
                return result[0]
        
        # Check by name + campus (if email not available)
        if campus_name:
            cursor.execute('''
                SELECT student_id FROM students 
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) 
                AND LOWER(TRIM(campus_name)) = LOWER(TRIM(?))
            ''', (name, campus_name))
            result = cursor.fetchone()
            if result:
                return result[0]
        
        # Last resort: check by name only (less reliable, but better than nothing)
        cursor.execute('''
            SELECT student_id FROM students 
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
        ''', (name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        
        return None
    
    def _insert_student(self, cursor, student_data: Dict):
        """Insert new student into database - all fields optional"""
        cursor.execute('''
            INSERT INTO students 
            (student_id, name, email, phone, campus_name, resume_url, status, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_data.get('student_id') or None,
            student_data.get('name') or 'Unknown',
            student_data.get('email') or None,
            student_data.get('phone') or None,
            student_data.get('campus_name') or None,
            student_data.get('resume_url') or None,
            student_data.get('status', 'active'),
            student_data.get('data_source', 'csv')
        ))
    
    def _update_student(self, cursor, student_data: Dict, existing_student_id: str = None):
        """Update existing student in database"""
        # Use provided existing_student_id or fall back to student_data['student_id']
        student_id = existing_student_id or student_data.get('student_id')
        
        if not student_id:
            raise ValueError("Cannot update student: no student_id provided")
        
        cursor.execute('''
            UPDATE students 
            SET name = COALESCE(?, name),
                email = COALESCE(?, email),
                phone = COALESCE(?, phone),
                campus_name = COALESCE(?, campus_name),
                resume_url = COALESCE(?, resume_url),
                status = COALESCE(?, status),
                last_updated = CURRENT_TIMESTAMP
            WHERE student_id = ?
        ''', (
            student_data.get('name'),
            student_data.get('email'),
            student_data.get('phone'),
            student_data.get('campus_name'),
            student_data.get('resume_url'),
            student_data.get('status'),
            student_id
        ))
    
    def _log_aggregation(self, source_type: str, source_path: str, processed: int,
                        added: int, updated: int, skipped: int, errors: List, 
                        execution_time: float):
        """Log aggregation activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_aggregation_logs
            (source_type, source_path, records_processed, records_added, 
             records_updated, records_skipped, errors, execution_time_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            source_type,
            source_path,
            processed,
            added,
            updated,
            skipped,
            json.dumps(errors),
            execution_time
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_students(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get all students with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM students WHERE 1=1'
        params = []
        
        if filters:
            if filters.get('student_id'):
                query += ' AND student_id = ?'
                params.append(filters['student_id'])
            
            if filters.get('campus_name'):
                query += ' AND campus_name = ?'
                params.append(filters['campus_name'])
            
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            
            if filters.get('category'):
                query += ' AND category = ?'
                params.append(filters['category'])
        
        query += ' ORDER BY name'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        students = []
        for row in rows:
            student = self._parse_student_row(row)
            students.append(student)
        
        conn.close()
        return students
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """Get a single student by student_id with all parsed data"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return self._parse_student_row(row)
        return None
    
    def _parse_student_row(self, row) -> Dict:
        """Parse a student row from database, including JSON fields and additional_info"""
        student = dict(row)
        
        # Parse JSON fields
        for json_field in ['skills', 'projects', 'certifications', 'education', 'languages']:
            if student.get(json_field):
                try:
                    student[json_field] = json.loads(student[json_field])
                except:
                    student[json_field] = []
            else:
                student[json_field] = []
        
        # Parse additional_info (Google Forms data)
        if student.get('additional_info'):
            try:
                additional_info = json.loads(student['additional_info'])
                # Merge additional_info fields into student dict for easier access
                for key, value in additional_info.items():
                    if key not in student or not student[key]:  # Don't overwrite existing data
                        student[key] = value
                student['additional_info_parsed'] = additional_info
            except:
                student['additional_info_parsed'] = {}
        else:
            student['additional_info_parsed'] = {}
        
        return student
    
    def _fetch_and_store_resume(self, cursor, student_id: str, resume_url: str):
        """Fetch resume text from URL and store in database"""
        try:
            from src.utils.resume_fetcher import ResumeFetcher
            fetcher = ResumeFetcher()
            resume_text = fetcher.fetch_resume_text(resume_url)
            
            if resume_text:
                # Store resume text in database
                cursor.execute('''
                    UPDATE students
                    SET resume_text = ?
                    WHERE student_id = ?
                ''', (resume_text[:50000], student_id))  # Limit to 50KB
                logger.info(f"Fetched and stored resume for student {student_id}")
            else:
                logger.warning(f"Could not fetch resume text from {resume_url}")
        except ImportError:
            logger.warning("Resume fetcher not available. Install PyPDF2: pip install PyPDF2")
        except Exception as e:
            logger.error(f"Error fetching resume: {e}")
    
    def export_to_csv(self, output_path: str, filters: Optional[Dict] = None) -> bool:
        """Export all students to CSV"""
        try:
            students = self.get_all_students(filters)
            df = pd.DataFrame(students)
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(students)} students to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_excel(self, output_path: str, filters: Optional[Dict] = None) -> bool:
        """Export all students to Excel"""
        try:
            students = self.get_all_students(filters)
            df = pd.DataFrame(students)
            df.to_excel(output_path, index=False, engine='openpyxl')
            logger.info(f"Exported {len(students)} students to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False

