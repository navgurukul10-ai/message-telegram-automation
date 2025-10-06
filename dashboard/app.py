"""
Web Dashboard for Telegram Job Fetcher
Beautiful UI to view all collected data
"""
from flask import Flask, render_template, jsonify
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PATHS, DATABASE

app = Flask(__name__)

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(PATHS['database'], DATABASE['name'])
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute("SELECT COUNT(*) FROM tech_jobs")
    tech_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM non_tech_jobs")
    non_tech_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM freelance_jobs")
    freelance_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM groups")
    groups_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tech_jobs WHERE is_verified = 1")
    verified_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(verification_score) FROM tech_jobs")
    avg_score = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'tech_jobs': tech_count,
        'non_tech_jobs': non_tech_count,
        'freelance_jobs': freelance_count,
        'total_groups': groups_count,
        'verified_jobs': verified_count,
        'avg_verification_score': round(avg_score, 2)
    })

@app.route('/api/daily_stats')
def get_daily_stats():
    """Get date-wise statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get data for last 30 days
    cursor.execute("""
        SELECT 
            DATE(created_at) as date,
            COUNT(DISTINCT CASE WHEN message_id IN (SELECT message_id FROM tech_jobs) THEN message_id END) as tech,
            COUNT(DISTINCT CASE WHEN message_id IN (SELECT message_id FROM non_tech_jobs) THEN message_id END) as non_tech,
            COUNT(DISTINCT CASE WHEN message_id IN (SELECT message_id FROM freelance_jobs) THEN message_id END) as freelance
        FROM messages
        WHERE created_at >= date('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """)
    
    daily_data = []
    for row in cursor.fetchall():
        daily_data.append({
            'date': row['date'],
            'tech': row['tech'],
            'non_tech': row['non_tech'],
            'freelance': row['freelance'],
            'total': row['tech'] + row['non_tech'] + row['freelance']
        })
    
    conn.close()
    return jsonify(daily_data)

@app.route('/api/groups_by_date')
def get_groups_by_date():
    """Get groups joined date-wise"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            DATE(join_date) as date,
            COUNT(*) as count,
            GROUP_CONCAT(group_name, ', ') as groups
        FROM groups
        WHERE join_date IS NOT NULL
        GROUP BY DATE(join_date)
        ORDER BY date DESC
    """)
    
    groups_data = []
    for row in cursor.fetchall():
        groups_data.append({
            'date': row['date'],
            'count': row['count'],
            'groups': row['groups']
        })
    
    conn.close()
    return jsonify(groups_data)

@app.route('/api/best_jobs')
def get_best_jobs():
    """Get best verified jobs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            message_text,
            company_name,
            company_website,
            skills_required,
            salary_range,
            job_location,
            work_mode,
            verification_score,
            date,
            group_name
        FROM tech_jobs
        WHERE is_verified = 1 
        AND company_name != ''
        ORDER BY verification_score DESC
        LIMIT 50
    """)
    
    jobs = []
    for row in cursor.fetchall():
        jobs.append({
            'message': row['message_text'][:200],
            'company': row['company_name'],
            'website': row['company_website'],
            'skills': row['skills_required'],
            'salary': row['salary_range'],
            'location': row['job_location'],
            'work_mode': row['work_mode'],
            'score': round(row['verification_score'], 2),
            'date': row['date'],
            'group': row['group_name']
        })
    
    conn.close()
    return jsonify(jobs)

@app.route('/api/messages/<job_type>')
def get_messages(job_type):
    """Get messages by type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    table_map = {
        'tech': 'tech_jobs',
        'non_tech': 'non_tech_jobs',
        'freelance': 'freelance_jobs'
    }
    
    table = table_map.get(job_type, 'tech_jobs')
    
    cursor.execute(f"""
        SELECT 
            message_text,
            company_name,
            skills_required,
            salary_range,
            work_mode,
            verification_score,
            date,
            group_name
        FROM {table}
        ORDER BY date DESC
        LIMIT 100
    """)
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'text': row['message_text'],
            'company': row['company_name'],
            'skills': row['skills_required'],
            'salary': row['salary_range'],
            'work_mode': row['work_mode'],
            'score': round(row['verification_score'], 2) if row['verification_score'] else 0,
            'date': row['date'],
            'group': row['group_name']
        })
    
    conn.close()
    return jsonify(messages)

if __name__ == '__main__':
    print("="*60)
    print("🌐 Starting Web Dashboard")
    print("="*60)
    print()
    print("Dashboard will open at: http://localhost:7000")
    print()
    print("Press Ctrl+C to stop")
    print("="*60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=7000)

