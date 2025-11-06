#!/usr/bin/env python3
"""
Fix Empty Job Types - Classify unclassified messages
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def classify_job_type(keywords, message_text):
    """Classify job based on keywords and message text"""
    keywords_lower = keywords.lower() if keywords else ''
    message_lower = message_text.lower() if message_text else ''
    
    # Tech keywords
    tech_keywords = [
        'developer', 'engineer', 'programming', 'software', 'python', 'java',
        'javascript', 'react', 'node', 'devops', 'data scientist', 'ml',
        'ai', 'machine learning', 'backend', 'frontend', 'fullstack',
        'full-stack', 'automation', 'qa', 'testing', 'cloud', 'aws'
    ]
    
    # Freelance keywords
    freelance_keywords = ['freelance', 'contract', 'consultant', 'remote freelance']
    
    # Check for tech
    for keyword in tech_keywords:
        if keyword in keywords_lower or keyword in message_lower:
            # Check if it's also freelance
            for fl_keyword in freelance_keywords:
                if fl_keyword in keywords_lower or fl_keyword in message_lower:
                    return 'freelance_tech'
            return 'tech'
    
    # Check for freelance non-tech
    for keyword in freelance_keywords:
        if keyword in keywords_lower or keyword in message_lower:
            return 'freelance'
    
    # Default to non_tech
    return 'non_tech'

def fix_empty_job_types():
    """Fix messages with empty job_type"""
    
    print("="*70)
    print("  🔧 FIXING EMPTY JOB TYPES")
    print("="*70)
    print()
    
    # Connect to database
    db_path = 'data/database/telegram_jobs.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get messages with empty job_type
    cursor.execute("""
        SELECT message_id, keywords_found, message_text
        FROM messages
        WHERE job_type IS NULL OR job_type = ''
    """)
    
    messages = cursor.fetchall()
    print(f"📊 Found {len(messages)} messages with empty job_type")
    print()
    
    # Classify and update
    updated = 0
    tech_count = 0
    non_tech_count = 0
    freelance_count = 0
    
    for msg_id, keywords, text in messages:
        job_type = classify_job_type(keywords, text)
        
        # Update in messages table
        cursor.execute("""
            UPDATE messages
            SET job_type = ?
            WHERE message_id = ?
        """, (job_type, msg_id))
        
        updated += 1
        
        if 'tech' in job_type:
            tech_count += 1
        elif job_type == 'freelance':
            freelance_count += 1
        else:
            non_tech_count += 1
        
        print(f"✅ {msg_id}: {job_type}")
    
    conn.commit()
    conn.close()
    
    print()
    print("="*70)
    print("  ✅ JOB TYPES FIXED!")
    print("="*70)
    print()
    print(f"📊 Classification Results:")
    print(f"   • Tech: {tech_count}")
    print(f"   • Non-Tech: {non_tech_count}")
    print(f"   • Freelance: {freelance_count}")
    print(f"   • Total Updated: {updated}")
    print()
    print("🎯 Now all messages are properly classified!")

if __name__ == "__main__":
    try:
        fix_empty_job_types()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

