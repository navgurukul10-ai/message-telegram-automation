"""
Terminal-based Dashboard
Simple text UI to view collected data
"""
import sqlite3
import os
from datetime import datetime
from config import PATHS, DATABASE

def print_header():
    """Print dashboard header"""
    print("\n" + "="*80)
    print(" "*20 + "📊 TELEGRAM JOB FETCHER DASHBOARD 📊")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%d %B %Y, %A')}")
    print(f"⏰ Time: {datetime.now().strftime('%I:%M %p')}")
    print("="*80 + "\n")

def get_overall_stats():
    """Get overall statistics"""
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the fetcher first!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│                          📈 OVERALL STATISTICS                              │")
    print("└─────────────────────────────────────────────────────────────────────────────┘\n")
    
    # Tech jobs
    cursor.execute("SELECT COUNT(*) FROM tech_jobs")
    tech = cursor.fetchone()[0]
    print(f"  🔧 Tech Jobs:          {tech:>6}")
    
    # Non-tech jobs
    cursor.execute("SELECT COUNT(*) FROM non_tech_jobs")
    non_tech = cursor.fetchone()[0]
    print(f"  💼 Non-Tech Jobs:      {non_tech:>6}")
    
    # Freelance jobs
    cursor.execute("SELECT COUNT(*) FROM freelance_jobs")
    freelance = cursor.fetchone()[0]
    print(f"  🏖️  Freelance Jobs:     {freelance:>6}")
    
    # Total
    total = tech + non_tech + freelance
    print(f"  {'─'*40}")
    print(f"  📊 Total Jobs:         {total:>6}")
    
    print()
    
    # Groups
    cursor.execute("SELECT COUNT(*) FROM groups")
    groups = cursor.fetchone()[0]
    print(f"  🔗 Groups Joined:      {groups:>6}")
    
    # Verified
    cursor.execute("SELECT COUNT(*) FROM tech_jobs WHERE is_verified = 1")
    verified = cursor.fetchone()[0]
    print(f"  ✅ Verified Jobs:      {verified:>6}")
    
    # Average score
    cursor.execute("SELECT AVG(verification_score) FROM tech_jobs")
    avg_score = cursor.fetchone()[0] or 0
    print(f"  ⭐ Avg Score:          {avg_score:>5.1f}%")
    
    print()
    conn.close()

def get_daily_stats():
    """Get date-wise statistics"""
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│                     📅 DATE-WISE JOB STATISTICS                             │")
    print("└─────────────────────────────────────────────────────────────────────────────┘\n")
    
    cursor.execute("""
        SELECT 
            DATE(created_at) as date,
            SUM(CASE WHEN message_id IN (SELECT message_id FROM tech_jobs) THEN 1 ELSE 0 END) as tech,
            SUM(CASE WHEN message_id IN (SELECT message_id FROM non_tech_jobs) THEN 1 ELSE 0 END) as non_tech,
            SUM(CASE WHEN message_id IN (SELECT message_id FROM freelance_jobs) THEN 1 ELSE 0 END) as freelance,
            COUNT(*) as total
        FROM messages
        WHERE created_at >= date('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 15
    """)
    
    rows = cursor.fetchall()
    
    if rows:
        print(f"  {'Date':<15} {'Tech':>8} {'Non-Tech':>10} {'Freelance':>10} {'Total':>8}")
        print(f"  {'-'*60}")
        
        for row in rows:
            date, tech, non_tech, freelance, total = row
            print(f"  {date:<15} {tech:>8} {non_tech:>10} {freelance:>10} {total:>8}")
    else:
        print("  No data available yet.")
    
    print()
    conn.close()

def get_groups_by_date():
    """Get groups joined date-wise"""
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│                    🔗 GROUPS JOINED (DATE-WISE)                             │")
    print("└─────────────────────────────────────────────────────────────────────────────┘\n")
    
    cursor.execute("""
        SELECT 
            DATE(join_date) as date,
            COUNT(*) as count,
            GROUP_CONCAT(group_name, ', ') as groups
        FROM groups
        WHERE join_date IS NOT NULL
        GROUP BY DATE(join_date)
        ORDER BY date DESC
        LIMIT 15
    """)
    
    rows = cursor.fetchall()
    
    if rows:
        print(f"  {'Date':<15} {'Count':>8}  {'Group Names':<50}")
        print(f"  {'-'*78}")
        
        for row in rows:
            date, count, groups = row
            # Truncate long group names
            groups_list = groups.split(', ')[:3]
            groups_str = ', '.join(groups_list)
            if len(groups.split(', ')) > 3:
                groups_str += f" ... +{len(groups.split(', ')) - 3} more"
            
            print(f"  {date:<15} {count:>8}  {groups_str:<50}")
    else:
        print("  No groups joined yet.")
    
    print()
    conn.close()

def get_best_jobs(limit=10):
    """Get top verified jobs"""
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print(f"│                     ⭐ BEST JOBS (TOP {limit})                                   │")
    print("└─────────────────────────────────────────────────────────────────────────────┘\n")
    
    cursor.execute(f"""
        SELECT 
            company_name,
            skills_required,
            salary_range,
            work_mode,
            verification_score,
            DATE(date) as date,
            group_name,
            message_text
        FROM tech_jobs
        WHERE is_verified = 1 
        AND company_name != ''
        ORDER BY verification_score DESC
        LIMIT {limit}
    """)
    
    rows = cursor.fetchall()
    
    if rows:
        for i, row in enumerate(rows, 1):
            company, skills, salary, work_mode, score, date, group, message = row
            
            print(f"  {i}. {company or 'Unknown Company'}")
            print(f"     ⭐ Score: {score:.1f}% | 📅 {date} | 🔗 {group}")
            
            if skills:
                print(f"     🔧 Skills: {skills}")
            if salary:
                print(f"     💰 Salary: {salary}")
            if work_mode:
                print(f"     🏠 Mode: {work_mode}")
            
            # Show first 150 chars of message
            msg_preview = message[:150].replace('\n', ' ') + '...'
            print(f"     📝 {msg_preview}")
            print()
    else:
        print("  No verified jobs yet.")
    
    conn.close()

def main_menu():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("  🎯 MENU OPTIONS")
        print("="*80)
        print()
        print("  1. 📊 Overall Statistics")
        print("  2. 📅 Date-wise Jobs")
        print("  3. 🔗 Groups Joined (Date-wise)")
        print("  4. ⭐ Best Jobs (Top 10)")
        print("  5. ⭐ Best Jobs (Top 50)")
        print("  6. 🔄 Refresh All")
        print("  7. ❌ Exit")
        print()
        
        try:
            choice = input("  Select option (1-7): ").strip()
            
            if choice == '1':
                get_overall_stats()
            elif choice == '2':
                get_daily_stats()
            elif choice == '3':
                get_groups_by_date()
            elif choice == '4':
                get_best_jobs(10)
            elif choice == '5':
                get_best_jobs(50)
            elif choice == '6':
                print_header()
                get_overall_stats()
                get_daily_stats()
                get_groups_by_date()
                get_best_jobs(10)
            elif choice == '7':
                print("\n  ✅ Goodbye!\n")
                break
            else:
                print("\n  ⚠️  Invalid choice. Try again.")
        
        except KeyboardInterrupt:
            print("\n\n  ✅ Goodbye!\n")
            break
        except Exception as e:
            print(f"\n  ❌ Error: {e}\n")

if __name__ == "__main__":
    print_header()
    get_overall_stats()
    get_daily_stats()
    get_groups_by_date()
    get_best_jobs(10)
    
    print("\n" + "="*80)
    print("  💡 For interactive menu, press Enter...")
    print("="*80)
    
    try:
        input()
        main_menu()
    except KeyboardInterrupt:
        print("\n  ✅ Goodbye!\n")

