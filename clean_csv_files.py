#!/usr/bin/env python3
"""
Clean CSV Files - Remove duplicates and keep only unique records
"""
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import PATHS, CSV_COLUMNS

def clean_csv_files():
    """Remove duplicates from CSV files"""
    
    print("="*70)
    print("  🧹 CLEANING CSV FILES")
    print("="*70)
    print()
    
    csv_files = ['tech_jobs.csv', 'non_tech_jobs.csv', 'freelance_jobs.csv']
    
    for filename in csv_files:
        filepath = os.path.join(PATHS['csv'], filename)
        
        if not os.path.exists(filepath):
            continue
            
        print(f"🧹 Cleaning {filename}...")
        
        # Read all records
        records = []
        seen_ids = set()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                message_id = row.get('message_id', '')
                if message_id and message_id not in seen_ids:
                    records.append(row)
                    seen_ids.add(message_id)
        
        # Write back unique records
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS['messages'])
            writer.writeheader()
            writer.writerows(records)
        
        print(f"   ✅ Kept {len(records)} unique records")
    
    print()
    print("="*70)
    print("  ✅ CSV FILES CLEANED!")
    print("="*70)
    print()
    
    # Show final counts
    for filename in csv_files:
        filepath = os.path.join(PATHS['csv'], filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"📄 {filename}: {len(lines)-1} unique records")

if __name__ == "__main__":
    try:
        clean_csv_files()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

