"""
Status checker for Telegram Job Fetcher
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PATHS, DATABASE

def check_status():
    """Check current status of the fetcher"""
    print("="*60)
    print("Telegram Job Fetcher - Status Report")
    print("="*60)
    print()
    
    # Check database
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    
    if not os.path.exists(db_path):
        print("❌ Database not found. System not initialized yet.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total messages from all tables
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    print(f"📊 Total Messages Fetched: {total_messages}")
    
    # Messages by category (from separate tables)
    print("\n📈 Jobs by Category (Separate Tables):")
    cursor.execute("SELECT COUNT(*) FROM tech_jobs")
    tech_count = cursor.fetchone()[0]
    print(f"   • Tech Jobs: {tech_count}")
    
    cursor.execute("SELECT COUNT(*) FROM non_tech_jobs")
    non_tech_count = cursor.fetchone()[0]
    print(f"   • Non-Tech Jobs: {non_tech_count}")
    
    cursor.execute("SELECT COUNT(*) FROM freelance_jobs")
    freelance_count = cursor.fetchone()[0]
    print(f"   • Freelance Jobs: {freelance_count}")
    
    # Verification stats
    print("\n✅ Verification Statistics:")
    cursor.execute("SELECT COUNT(*) FROM tech_jobs WHERE is_verified = 1")
    verified_tech = cursor.fetchone()[0]
    print(f"   • Verified Tech Jobs: {verified_tech}/{tech_count}")
    
    cursor.execute("SELECT AVG(verification_score) FROM tech_jobs")
    avg_score = cursor.fetchone()[0]
    if avg_score:
        print(f"   • Average Verification Score: {avg_score:.2f}%")
    
    # Jobs with company info
    cursor.execute("SELECT COUNT(*) FROM tech_jobs WHERE company_name != ''")
    with_company = cursor.fetchone()[0]
    print(f"   • Jobs with Company Name: {with_company}/{tech_count}")
    
    # Total groups
    cursor.execute("SELECT COUNT(*) FROM groups")
    total_groups = cursor.fetchone()[0]
    print(f"\n🔗 Total Groups Joined: {total_groups}")
    
    # Recent groups
    print("\n📅 Recently Joined Groups:")
    cursor.execute("SELECT group_name, join_date FROM groups ORDER BY join_date DESC LIMIT 5")
    for name, date in cursor.fetchall():
        print(f"   • {name} - {date}")
    
    # Daily stats (last 7 days)
    print("\n📆 Last 7 Days Statistics:")
    cursor.execute("""
        SELECT date, groups_joined, messages_fetched, tech_jobs, 
               non_tech_jobs, freelance_jobs 
        FROM daily_stats 
        ORDER BY date DESC 
        LIMIT 7
    """)
    
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"   {row[0]}: {row[1]} groups, {row[2]} messages "
                  f"(Tech: {row[3]}, Non-Tech: {row[4]}, Freelance: {row[5]})")
    else:
        print("   No daily statistics yet")
    
    # Account usage today
    print("\n👥 Account Usage Today:")
    today = datetime.now().date()
    cursor.execute("""
        SELECT account_name, groups_joined, messages_fetched 
        FROM account_usage 
        WHERE date = ?
    """, (today,))
    
    rows = cursor.fetchall()
    if rows:
        for name, groups, messages in rows:
            print(f"   • {name}: {groups} groups, {messages} messages")
    else:
        print("   No activity today yet")
    
    # Check CSV files
    print("\n📁 CSV Files:")
    csv_dir = PATHS['csv']
    if os.path.exists(csv_dir):
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        for f in csv_files:
            file_path = os.path.join(csv_dir, f)
            size = os.path.getsize(file_path)
            print(f"   • {f}: {size:,} bytes")
    else:
        print("   CSV directory not found")
    
    # Check logs
    print("\n📝 Recent Logs:")
    logs_dir = PATHS['logs']
    if os.path.exists(logs_dir):
        log_files = sorted([f for f in os.listdir(logs_dir) if f.endswith('.log')])
        for f in log_files[-3:]:
            print(f"   • {f}")
    else:
        print("   Logs directory not found")
    
    conn.close()
    
    print()
    print("="*60)
    print("✅ Status check complete!")
    print("="*60)

if __name__ == "__main__":
    try:
        check_status()
    except Exception as e:
        print(f"❌ Error checking status: {e}")

