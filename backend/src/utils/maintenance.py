"""
Maintenance utilities for automatic database and CSV synchronization
"""
import csv
import sqlite3
import os
from datetime import datetime

from config.settings import PATHS, DATABASE
from src.services.classifier import MessageClassifier
from src.utils.logger import get_logger

logger = get_logger('maintenance')


def fix_empty_job_types(db_path=None):
    """
    Re-classify all messages with empty job_type
    Returns: (fixed_count, skipped_count)
    """
    if db_path is None:
        db_path = os.path.join(PATHS['database'], DATABASE['name'])
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all messages with empty or null job_type
        cursor.execute('''
            SELECT message_id, message_text 
            FROM messages 
            WHERE job_type IS NULL OR job_type = ''
        ''')
        
        messages = cursor.fetchall()
        total = len(messages)
        
        if total == 0:
            logger.info("All messages already have job_type")
            conn.close()
            return 0, 0
        
        logger.info(f"Found {total} messages with empty job_type, fixing...")
        
        # Initialize classifier
        classifier = MessageClassifier()
        
        # Process each message
        fixed = 0
        skipped = 0
        
        for message_id, message_text in messages:
            try:
                # Classify the message
                job_type, keywords = classifier.classify(message_text)
                
                if job_type:
                    # Update the message with job_type
                    keywords_str = ','.join(keywords) if keywords else ''
                    
                    cursor.execute('''
                        UPDATE messages 
                        SET job_type = ?, keywords_found = ?
                        WHERE message_id = ?
                    ''', (job_type, keywords_str, message_id))
                    
                    fixed += 1
                else:
                    skipped += 1
            
            except Exception as e:
                logger.error(f"Error processing message {message_id}: {e}")
                skipped += 1
        
        # Commit changes
        conn.commit()
        
        # Copy to category-specific tables
        _sync_category_tables(conn)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Fixed {fixed} messages, skipped {skipped}")
        return fixed, skipped
    
    except Exception as e:
        logger.error(f"Error fixing job types: {e}")
        return 0, 0


def _sync_category_tables(conn):
    """Sync category-specific tables from messages table"""
    cursor = conn.cursor()
    
    # Tech jobs
    cursor.execute('''
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used, job_type
        FROM messages 
        WHERE job_type LIKE '%tech%' AND job_type NOT LIKE '%non_tech%'
    ''')
    tech_messages = cursor.fetchall()
    
    for msg in tech_messages:
        cursor.execute('''
            INSERT OR IGNORE INTO tech_jobs 
            (message_id, group_name, group_link, sender, date, message_text,
             keywords_found, account_used, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', msg)
    
    # Non-tech jobs
    cursor.execute('''
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used, job_type
        FROM messages 
        WHERE job_type = 'non_tech'
    ''')
    non_tech_messages = cursor.fetchall()
    
    for msg in non_tech_messages:
        cursor.execute('''
            INSERT OR IGNORE INTO non_tech_jobs 
            (message_id, group_name, group_link, sender, date, message_text,
             keywords_found, account_used, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', msg)
    
    # Freelance jobs
    cursor.execute('''
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used, job_type
        FROM messages 
        WHERE job_type LIKE '%freelance%'
    ''')
    freelance_messages = cursor.fetchall()
    
    for msg in freelance_messages:
        cursor.execute('''
            INSERT OR IGNORE INTO freelance_jobs 
            (message_id, group_name, group_link, sender, date, message_text,
             keywords_found, account_used, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', msg)
    
    logger.debug("Category tables synced")


def backup_csv_file(path):
    """Create timestamped backup of CSV file and cleanup old backups"""
    if os.path.exists(path):
        ts = int(datetime.now().timestamp())
        backup_path = f"{path}.backup.{ts}"
        os.replace(path, backup_path)
        logger.debug(f"Created backup: {backup_path}")
        
        # Auto-cleanup: Delete backups older than 3 days
        cleanup_old_backups(path, days=3)


def cleanup_old_backups(original_path, days=3):
    """Delete backup files older than specified days"""
    import glob
    import time
    
    # Find all backup files for this CSV
    backup_pattern = f"{original_path}.backup.*"
    backup_files = glob.glob(backup_pattern)
    
    if not backup_files:
        return
    
    # Current time
    now = time.time()
    cutoff = now - (days * 24 * 60 * 60)  # days to seconds
    
    deleted_count = 0
    for backup_file in backup_files:
        try:
            # Extract timestamp from filename
            parts = backup_file.split('.backup.')
            if len(parts) == 2:
                backup_ts = int(parts[1])
                
                # Delete if older than cutoff
                if backup_ts < cutoff:
                    os.remove(backup_file)
                    deleted_count += 1
                    logger.debug(f"Deleted old backup: {backup_file}")
        except (ValueError, OSError) as e:
            logger.debug(f"Error processing backup {backup_file}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} old backup(s) for {os.path.basename(original_path)}")


def export_query_to_csv(conn, query, out_path):
    """Export SQL query results to CSV"""
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    
    # Backup then write
    backup_csv_file(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    return len(rows)


def sync_csv_with_database(db_path=None):
    """
    Export all database tables to CSV files
    Returns: dict with counts of exported rows
    """
    if db_path is None:
        db_path = os.path.join(PATHS['database'], DATABASE['name'])
    
    csv_dir = PATHS['csv']
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        
        results = {}
        
        # 1) all_messages.csv
        all_messages_q = """
            SELECT message_id, group_name, group_link, sender, date, message_text,
                   keywords_found, account_used, job_type
            FROM messages
            ORDER BY date DESC
        """
        count_all = export_query_to_csv(conn, all_messages_q, os.path.join(csv_dir, "all_messages.csv"))
        results['all_messages'] = count_all
        logger.info(f"✅ all_messages.csv: {count_all} rows")
        
        # 2) tech_jobs.csv
        tech_q = """
            SELECT message_id, group_name, group_link, sender, date, message_text,
                   keywords_found, account_used, job_type
            FROM messages
            WHERE job_type LIKE '%tech%' AND job_type NOT LIKE '%non_tech%'
            ORDER BY date DESC
        """
        count_tech = export_query_to_csv(conn, tech_q, os.path.join(csv_dir, "tech_jobs.csv"))
        results['tech_jobs'] = count_tech
        logger.info(f"✅ tech_jobs.csv: {count_tech} rows")
        
        # 3) non_tech_jobs.csv
        non_tech_q = """
            SELECT message_id, group_name, group_link, sender, date, message_text,
                   keywords_found, account_used, job_type
            FROM messages
            WHERE job_type = 'non_tech'
            ORDER BY date DESC
        """
        count_non = export_query_to_csv(conn, non_tech_q, os.path.join(csv_dir, "non_tech_jobs.csv"))
        results['non_tech_jobs'] = count_non
        logger.info(f"✅ non_tech_jobs.csv: {count_non} rows")
        
        # 4) freelance_jobs.csv
        freelance_q = """
            SELECT message_id, group_name, group_link, sender, date, message_text,
                   keywords_found, account_used, job_type
            FROM messages
            WHERE job_type LIKE '%freelance%'
            ORDER BY date DESC
        """
        count_free = export_query_to_csv(conn, freelance_q, os.path.join(csv_dir, "freelance_jobs.csv"))
        results['freelance_jobs'] = count_free
        logger.info(f"✅ freelance_jobs.csv: {count_free} rows")
        
        # 5) fresher_jobs.csv
        fresher_q = """
            SELECT message_id, group_name, group_link, sender, date, message_text,
                   keywords_found, account_used, job_type
            FROM messages
            WHERE job_type LIKE '%fresher%'
            ORDER BY date DESC
        """
        count_fresher = export_query_to_csv(conn, fresher_q, os.path.join(csv_dir, "fresher_jobs.csv"))
        results['fresher_jobs'] = count_fresher
        logger.info(f"✅ fresher_jobs.csv: {count_fresher} rows")
        
        # 6) joined_groups.csv
        groups_q = """
            SELECT group_name, group_link, join_date
            FROM groups
            WHERE join_date IS NOT NULL
            ORDER BY join_date DESC
        """
        count_groups = export_query_to_csv(conn, groups_q, os.path.join(csv_dir, "joined_groups.csv"))
        results['joined_groups'] = count_groups
        logger.info(f"✅ joined_groups.csv: {count_groups} rows")
        
        conn.close()
        
        logger.info("CSV sync completed successfully")
        return results
    
    except Exception as e:
        logger.error(f"Error syncing CSV: {e}")
        return None


def perform_maintenance():
    """
    Perform all maintenance tasks:
    1. Fix empty job types
    2. Sync CSV files with database
    
    Returns: dict with maintenance results
    """
    logger.info("="*60)
    logger.info("🔧 Starting Automatic Maintenance")
    logger.info("="*60)
    
    results = {}
    
    # Step 1: Fix empty job types
    logger.info("Step 1: Fixing empty job types...")
    fixed, skipped = fix_empty_job_types()
    results['job_types_fixed'] = fixed
    results['job_types_skipped'] = skipped
    
    # Step 2: Sync CSV files
    logger.info("Step 2: Syncing CSV files with database...")
    csv_results = sync_csv_with_database()
    if csv_results:
        results['csv_sync'] = csv_results
    
    logger.info("="*60)
    logger.info("✅ Maintenance Completed")
    logger.info("="*60)
    
    return results

