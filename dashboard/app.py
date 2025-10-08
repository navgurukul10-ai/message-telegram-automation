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
from src.services.job_scorer import JobQualityScorer

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
    # Get counts from messages table
    cursor.execute("SELECT COUNT(*) FROM messages WHERE job_type LIKE '%tech%' AND job_type NOT LIKE '%non_tech%'")
    tech_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages WHERE job_type = 'non_tech'")
    non_tech_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages WHERE job_type LIKE '%freelance%'")
    freelance_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM groups")
    groups_count = cursor.fetchone()[0]
    
    # Since we don't have verification_score in messages table
    verified_count = 0
    avg_score = 0
    
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
    """Get date-wise statistics based on when messages were fetched"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get data for last 30 days using created_at (fetch date) and job_type column
    cursor.execute("""
        SELECT 
            DATE(created_at) as date,
            COUNT(CASE WHEN job_type LIKE '%tech%' AND job_type NOT LIKE '%non_tech%' THEN 1 END) as tech,
            COUNT(CASE WHEN job_type = 'non_tech' THEN 1 END) as non_tech,
            COUNT(CASE WHEN job_type LIKE '%freelance%' THEN 1 END) as freelance,
            COUNT(*) as total_fetched
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
    """Get best quality jobs (score >= 60) - both tech and non-tech"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all recent jobs
    cursor.execute("""
        SELECT 
            message_text,
            job_type,
            keywords_found,
            date,
            group_name,
            sender,
            account_used
        FROM messages
        WHERE job_type IS NOT NULL 
        AND job_type != ''
        ORDER BY date DESC
        LIMIT 200
    """)
    
    # Score each job
    scorer = JobQualityScorer()
    scored_jobs = []
    
    for row in cursor.fetchall():
        message_text = row['message_text']
        score_result = scorer.score_job(message_text)

        # Additional strict backend safeguard: if message mentions international
        # locations but has no remote/WFH keywords, exclude from best jobs
        msg_lower = (message_text or '').lower()
        international_keywords = [
            'usa', 'us', 'united states', 'uk', 'united kingdom', 'singapore', 'dubai', 'uae',
            'canada', 'australia', 'germany', 'netherlands', 'europe', 'london', 'new york',
            'san francisco', 'toronto', 'sydney', 'melbourne', 'algeria', 'algiers', 'france',
            'spain', 'italy', 'japan', 'china', 'brazil', 'mexico', 'south africa', 'egypt',
            'turkey', 'russia', 'poland', 'sweden', 'norway', 'denmark', 'finland', 'belgium',
            'switzerland', 'austria', 'ireland', 'portugal', 'greece', 'czech', 'hungary',
            'romania', 'bulgaria', 'croatia', 'slovenia', 'slovakia', 'estonia', 'latvia',
            'lithuania', 'malta', 'cyprus', 'luxembourg', 'iceland', 'new zealand', 'south korea',
            'thailand', 'vietnam', 'philippines', 'indonesia', 'malaysia', 'taiwan', 'hong kong',
            'israel', 'saudi arabia', 'qatar', 'kuwait', 'bahrain', 'oman', 'jordan', 'lebanon',
            'argentina', 'chile', 'colombia', 'peru', 'venezuela', 'uruguay', 'paraguay',
            'bolivia', 'ecuador', 'guyana', 'suriname', 'trinidad', 'jamaica', 'cuba',
            'dominican republic', 'haiti', 'panama', 'costa rica', 'guatemala', 'honduras',
            'nicaragua', 'el salvador', 'belize', 'bahamas', 'barbados', 'antigua', 'grenada',
            'st. lucia', 'st. vincent', 'dominica', 'st. kitts', 'nevis', 'montserrat',
            'anguilla', 'british virgin islands', 'us virgin islands', 'puerto rico',
            'cayman islands', 'bermuda', 'turks and caicos', 'aruba', 'curacao', 'bonaire',
            'sint maarten', 'saba', 'sint eustatius', 'greenland', 'faroe islands'
        ]
        remote_keywords = ['remote', 'wfh', 'work from home', 'work-from-home', 'hybrid']
        is_international_msg = any(k in msg_lower for k in international_keywords)
        has_remote_msg = any(k in msg_lower for k in remote_keywords)

        # If international mentioned but no remote, force skip regardless of score
        if is_international_msg and not has_remote_msg:
            continue

        # Only include jobs with score >= 60
        if score_result['total_score'] >= 60:
            scored_jobs.append({
                'message': row['message_text'],
                'company': score_result['company_name'] or 'Company Not Specified',
                'skills': score_result['skills_info'] or row['keywords_found'],
                'salary': score_result['salary_info'] or '',
                'work_mode': 'Remote' if score_result['has_remote'] else '',
                'location': score_result['location_info'] or '',
                'score': score_result['total_score'],
                'date': row['date'],
                'group': row['group_name'],
                'apply_link': score_result['apply_link']
            })
    
    # Sort by score (highest first)
    scored_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 50
    conn.close()
    return jsonify(scored_jobs[:50])

@app.route('/api/messages/<job_type>')
def get_messages(job_type):
    """Get messages by type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query messages table based on job_type
    if job_type == 'tech':
        cursor.execute("""
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE job_type LIKE '%tech%' AND job_type NOT LIKE '%non_tech%'
            ORDER BY date DESC
            LIMIT 100
        """)
    elif job_type == 'non_tech':
        cursor.execute("""
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE job_type = 'non_tech'
            ORDER BY date DESC
            LIMIT 100
        """)
    elif job_type == 'freelance':
        cursor.execute("""
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE job_type LIKE '%freelance%'
            ORDER BY date DESC
            LIMIT 100
        """)
    else:
        # Default to tech
        cursor.execute("""
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE job_type LIKE '%tech%' AND job_type NOT LIKE '%non_tech%'
            ORDER BY date DESC
            LIMIT 100
        """)
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'text': row['message_text'],
            'company': 'Company Not Specified',  # Extract from message if needed
            'skills': row['keywords_found'],
            'salary': '',  # Extract from message if needed
            'work_mode': '',  # Extract from message if needed
            'score': 0,  # No verification score available
            'date': row['date'],
            'group': row['group_name']
        })
    
    conn.close()
    return jsonify(messages)

@app.route('/api/group_details/<group_name>')
def get_group_details(group_name):
    """Get detailed information about a specific group"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all messages from this group
    cursor.execute("""
        SELECT 
            message_text,
            date,
            job_type,
            keywords_found
        FROM messages
        WHERE group_name = ?
        ORDER BY date DESC
    """, (group_name,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'text': row['message_text'],
            'date': row['date'],
            'job_type': row['job_type'],
            'keywords': row['keywords_found']
        })
    
    # Get first and last message dates
    first_message = "N/A"
    last_message = "N/A"
    
    if messages:
        first_message = messages[-1]['date'][:10]  # First message (oldest)
        last_message = messages[0]['date'][:10]    # Last message (newest)
    
    conn.close()
    
    return jsonify({
        'messages': messages,
        'firstMessage': first_message,
        'lastMessage': last_message,
        'totalCount': len(messages)
    })

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

