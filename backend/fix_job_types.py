#!/usr/bin/env python3
"""
Fix empty job_type in existing messages
Re-classify all messages that have keywords but no job_type
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.classifier import MessageClassifier
from src.utils.logger import get_logger

logger = get_logger('fix_job_types')

def fix_job_types():
    """Re-classify all messages with empty job_type"""
    
    print("="*70)
    print("  🔧 FIXING JOB TYPES IN DATABASE")
    print("="*70)
    print()
    
    # Connect to database
    db_path = 'data/database/telegram_jobs.db'
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
    
    print(f"📊 Found {total} messages with empty job_type")
    print()
    
    if total == 0:
        print("✅ All messages already have job_type!")
        conn.close()
        return
    
    # Initialize classifier
    classifier = MessageClassifier()
    
    # Process each message
    fixed = 0
    tech_count = 0
    non_tech_count = 0
    freelance_count = 0
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
                
                # Count by type
                if 'tech' in job_type:
                    tech_count += 1
                elif 'non_tech' in job_type:
                    non_tech_count += 1
                elif 'freelance' in job_type:
                    freelance_count += 1
                
                if fixed % 10 == 0:
                    print(f"  ✓ Processed {fixed}/{total}...")
            else:
                skipped += 1
        
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            skipped += 1
    
    # Commit changes
    conn.commit()
    
    # Now copy to category-specific tables
    print()
    print("📋 Copying to category-specific tables...")
    
    # Get tech messages and insert with proper columns
    cursor.execute('''
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used
        FROM messages WHERE job_type LIKE '%tech%'
    ''')
    tech_messages = cursor.fetchall()
    
    for msg in tech_messages:
        cursor.execute('''
            INSERT OR IGNORE INTO tech_jobs 
            (message_id, group_name, group_link, sender, date, message_text,
             keywords_found, account_used, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'tech')
        ''', msg)
    
    # Get non-tech messages
    cursor.execute('''
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used
        FROM messages WHERE job_type LIKE '%non_tech%'
    ''')
    non_tech_messages = cursor.fetchall()
    
    for msg in non_tech_messages:
        cursor.execute('''
            INSERT OR IGNORE INTO non_tech_jobs 
            (message_id, group_name, group_link, sender, date, message_text,
             keywords_found, account_used, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'non_tech')
        ''', msg)
    
    # Get freelance messages
    cursor.execute('''
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used
        FROM messages WHERE job_type LIKE '%freelance%'
    ''')
    freelance_messages = cursor.fetchall()
    
    for msg in freelance_messages:
        cursor.execute('''
            INSERT OR IGNORE INTO freelance_jobs 
            (message_id, group_name, group_link, sender, date, message_text,
             keywords_found, account_used, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'freelance')
        ''', msg)
    
    conn.commit()
    conn.close()
    
    print()
    print("="*70)
    print("  ✅ FIX COMPLETE!")
    print("="*70)
    print()
    print(f"📊 Results:")
    print(f"   • Total messages processed: {total}")
    print(f"   • Fixed with job_type: {fixed}")
    print(f"   • Skipped (not jobs): {skipped}")
    print()
    print(f"📈 Jobs by category:")
    print(f"   • Tech Jobs: {tech_count}")
    print(f"   • Non-Tech Jobs: {non_tech_count}")
    print(f"   • Freelance Jobs: {freelance_count}")
    print()
    print("🎯 Now run: python3 check_status.py")
    print()

if __name__ == "__main__":
    try:
        fix_job_types()
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Fix failed: {e}")
        sys.exit(1)

