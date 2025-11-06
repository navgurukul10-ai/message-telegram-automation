#!/usr/bin/env python3
"""
Fix CSV Files - Copy data from database to category-specific CSV files
"""
import sqlite3
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import PATHS, CSV_COLUMNS

def fix_csv_files():
    """Copy data from database to CSV files"""
    
    print("="*70)
    print("  🔧 FIXING CSV FILES")
    print("="*70)
    print()
    
    # Connect to database
    db_path = 'data/database/telegram_jobs.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all messages
    cursor.execute("""
        SELECT message_id, group_name, group_link, sender, date, 
               message_text, job_type, keywords_found, account_used
        FROM messages
        ORDER BY date DESC
    """)
    
    messages = cursor.fetchall()
    print(f"📊 Found {len(messages)} messages in database")
    
    # Clear and recreate CSV files
    csv_files = {
        'tech_jobs.csv': [],
        'non_tech_jobs.csv': [],
        'freelance_jobs.csv': []
    }
    
    # Categorize messages
    for msg in messages:
        message_data = {
            'message_id': msg[0],
            'group_name': msg[1],
            'group_link': msg[2],
            'sender': msg[3],
            'date': msg[4],
            'message_text': msg[5],
            'job_type': msg[6],
            'keywords_found': msg[7],
            'account_used': msg[8]
        }
        
        job_type = msg[6].lower() if msg[6] else ''
        
        if 'tech' in job_type:
            csv_files['tech_jobs.csv'].append(message_data)
        
        if 'non_tech' in job_type:
            csv_files['non_tech_jobs.csv'].append(message_data)
        
        if 'freelance' in job_type:
            csv_files['freelance_jobs.csv'].append(message_data)
    
    # Write to CSV files
    for filename, data in csv_files.items():
        filepath = os.path.join(PATHS['csv'], filename)
        
        print(f"📝 Writing {len(data)} records to {filename}")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS['messages'])
            writer.writeheader()
            
            for row in data:
                # Filter data to only include columns defined in the schema
                filtered_data = {k: v for k, v in row.items() if k in CSV_COLUMNS['messages']}
                
                # Fill missing columns with empty strings
                for col in CSV_COLUMNS['messages']:
                    if col not in filtered_data:
                        filtered_data[col] = ''
                
                writer.writerow(filtered_data)
    
    conn.close()
    
    print()
    print("="*70)
    print("  ✅ CSV FILES FIXED!")
    print("="*70)
    print()
    
    # Show final counts
    for filename in csv_files.keys():
        filepath = os.path.join(PATHS['csv'], filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"📄 {filename}: {len(lines)-1} records (excluding header)")
    
    print()
    print("🎯 Now your CSV files have all the data!")

if __name__ == "__main__":
    try:
        fix_csv_files()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

