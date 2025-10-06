"""
Generate comprehensive reports from collected data
"""
import sqlite3
import os
import csv
from datetime import datetime, timedelta
from config import PATHS, DATABASE

def generate_report(days=7):
    """Generate a comprehensive report"""
    
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the fetcher first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    report_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(PATHS['csv'], f'report_{report_date}.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"TELEGRAM JOB FETCHER - COMPREHENSIVE REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        
        # Summary Statistics
        f.write("📊 SUMMARY STATISTICS\n")
        f.write("-"*70 + "\n")
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        f.write(f"Total Job Messages: {total_messages}\n")
        
        cursor.execute("SELECT COUNT(DISTINCT group_name) FROM messages")
        active_groups = cursor.fetchone()[0]
        f.write(f"Active Groups with Jobs: {active_groups}\n")
        
        cursor.execute("SELECT COUNT(*) FROM groups")
        total_groups = cursor.fetchone()[0]
        f.write(f"Total Groups Joined: {total_groups}\n\n")
        
        # Job Type Breakdown
        f.write("📈 JOB TYPE BREAKDOWN\n")
        f.write("-"*70 + "\n")
        cursor.execute("SELECT job_type, COUNT(*) FROM messages GROUP BY job_type ORDER BY COUNT(*) DESC")
        for job_type, count in cursor.fetchall():
            percentage = (count / total_messages * 100) if total_messages > 0 else 0
            f.write(f"{job_type:20s}: {count:5d} ({percentage:5.2f}%)\n")
        f.write("\n")
        
        # Top Groups by Job Count
        f.write("🏆 TOP 10 GROUPS BY JOB COUNT\n")
        f.write("-"*70 + "\n")
        cursor.execute("""
            SELECT group_name, COUNT(*) as job_count 
            FROM messages 
            GROUP BY group_name 
            ORDER BY job_count DESC 
            LIMIT 10
        """)
        for i, (name, count) in enumerate(cursor.fetchall(), 1):
            f.write(f"{i:2d}. {name:40s}: {count:4d} jobs\n")
        f.write("\n")
        
        # Daily Trend (Last N days)
        f.write(f"📅 DAILY TREND (LAST {days} DAYS)\n")
        f.write("-"*70 + "\n")
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT DATE(date) as day, COUNT(*) as count
            FROM messages
            WHERE date >= ?
            GROUP BY day
            ORDER BY day DESC
        """, (cutoff_date,))
        
        daily_data = cursor.fetchall()
        if daily_data:
            for day, count in daily_data:
                f.write(f"{day}: {count:4d} jobs\n")
        else:
            f.write("No data available\n")
        f.write("\n")
        
        # Top Keywords Found
        f.write("🔑 TOP KEYWORDS FOUND\n")
        f.write("-"*70 + "\n")
        cursor.execute("SELECT keywords_found FROM messages WHERE keywords_found != ''")
        
        keyword_count = {}
        for row in cursor.fetchall():
            keywords = row[0].split(',')
            for kw in keywords:
                kw = kw.strip()
                keyword_count[kw] = keyword_count.get(kw, 0) + 1
        
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:20]
        for kw, count in sorted_keywords:
            f.write(f"{kw:30s}: {count:4d}\n")
        f.write("\n")
        
        # Account Usage Summary
        f.write("👥 ACCOUNT USAGE SUMMARY\n")
        f.write("-"*70 + "\n")
        cursor.execute("""
            SELECT account_name, 
                   SUM(groups_joined) as total_groups,
                   SUM(messages_fetched) as total_messages
            FROM account_usage
            GROUP BY account_name
        """)
        
        for account, groups, messages in cursor.fetchall():
            f.write(f"{account:20s}: {groups:3d} groups, {messages:5d} messages\n")
        f.write("\n")
        
        # Recent Activity
        f.write("🕒 RECENT ACTIVITY (Last 24 hours)\n")
        f.write("-"*70 + "\n")
        cutoff_time = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            SELECT COUNT(*) FROM messages WHERE created_at >= ?
        """, (cutoff_time,))
        recent_count = cursor.fetchone()[0]
        f.write(f"New jobs in last 24h: {recent_count}\n\n")
        
        f.write("="*70 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*70 + "\n")
    
    conn.close()
    
    print(f"✅ Report generated: {report_file}")
    print(f"\nQuick Summary:")
    print(f"- Total Jobs: {total_messages}")
    print(f"- Active Groups: {active_groups}")
    print(f"- Report saved to: {report_file}")
    
    return report_file

def export_top_groups_csv():
    """Export top groups to a separate CSV"""
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    output_file = os.path.join(PATHS['csv'], f'top_groups_{datetime.now().strftime("%Y%m%d")}.csv')
    
    cursor.execute("""
        SELECT 
            g.group_name,
            g.group_link,
            COUNT(m.id) as job_count,
            MAX(m.date) as last_job_date,
            g.join_date
        FROM groups g
        LEFT JOIN messages m ON g.group_link = m.group_link
        GROUP BY g.group_link
        ORDER BY job_count DESC
    """)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Group Name', 'Group Link', 'Job Count', 'Last Job Date', 'Join Date'])
        writer.writerows(cursor.fetchall())
    
    conn.close()
    print(f"✅ Top groups exported to: {output_file}")

if __name__ == "__main__":
    import sys
    
    days = 7
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except:
            pass
    
    print("Generating report...")
    generate_report(days)
    
    print("\nExporting top groups...")
    export_top_groups_csv()
    
    print("\n✨ Done!")

