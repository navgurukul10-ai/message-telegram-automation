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
from src.services.company_extractor import JobQualityScorer

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
    cursor.execute("SELECT COUNT(*) FROM messages WHERE job_type = 'tech'")
    tech_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages WHERE job_type = 'non_tech'")
    non_tech_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages WHERE job_type LIKE '%freelance%'")
    freelance_count = cursor.fetchone()[0]
    
    # Enhanced fresher count with comprehensive detection
    cursor.execute("""
        SELECT COUNT(*) FROM messages 
        WHERE (
            job_type LIKE '%fresher%' OR
            job_type LIKE '%entry%' OR
            job_type LIKE '%graduate%' OR
            job_type LIKE '%trainee%' OR
            job_type LIKE '%junior%' OR
            job_type LIKE '%intern%' OR
            job_type LIKE '%0-1%' OR
            job_type LIKE '%0-3%' OR
            job_type LIKE '%1-2%' OR
            job_type LIKE '%1-3%' OR
            LOWER(message_text) LIKE '%fresher%' OR
            LOWER(message_text) LIKE '%entry level%' OR
            LOWER(message_text) LIKE '%entry-level%' OR
            LOWER(message_text) LIKE '%graduate%' OR
            LOWER(message_text) LIKE '%trainee%' OR
            LOWER(message_text) LIKE '%junior%' OR
            LOWER(message_text) LIKE '%intern%' OR
            LOWER(message_text) LIKE '%0-1 years%' OR
            LOWER(message_text) LIKE '%0-3 years%' OR
            LOWER(message_text) LIKE '%1-2 years%' OR
            LOWER(message_text) LIKE '%1-3 years%' OR
            LOWER(message_text) LIKE '%0 to 1%' OR
            LOWER(message_text) LIKE '%0 to 3%' OR
            LOWER(message_text) LIKE '%1 to 2%' OR
            LOWER(message_text) LIKE '%1 to 3%' OR
            LOWER(message_text) LIKE '%no experience%' OR
            LOWER(message_text) LIKE '%new graduate%' OR
            LOWER(message_text) LIKE '%recent graduate%' OR
            LOWER(message_text) LIKE '%fresh graduate%' OR
            LOWER(message_text) LIKE '%freshers welcome%' OR
            LOWER(message_text) LIKE '%beginners welcome%' OR
            LOWER(message_text) LIKE '%training provided%' OR
            LOWER(message_text) LIKE '%mentorship%' OR
            LOWER(message_text) LIKE '%entry position%'
        )
    """)
    fresher_count = cursor.fetchone()[0]
    
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
        'fresher_jobs': fresher_count,
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
            COUNT(CASE WHEN (
                job_type LIKE '%fresher%' OR
                job_type LIKE '%entry%' OR
                job_type LIKE '%graduate%' OR
                job_type LIKE '%trainee%' OR
                job_type LIKE '%junior%' OR
                job_type LIKE '%intern%' OR
                job_type LIKE '%0-1%' OR
                job_type LIKE '%0-3%' OR
                job_type LIKE '%1-2%' OR
                job_type LIKE '%1-3%' OR
                LOWER(message_text) LIKE '%fresher%' OR
                LOWER(message_text) LIKE '%entry level%' OR
                LOWER(message_text) LIKE '%entry-level%' OR
                LOWER(message_text) LIKE '%graduate%' OR
                LOWER(message_text) LIKE '%trainee%' OR
                LOWER(message_text) LIKE '%junior%' OR
                LOWER(message_text) LIKE '%intern%' OR
                LOWER(message_text) LIKE '%0-1 years%' OR
                LOWER(message_text) LIKE '%0-3 years%' OR
                LOWER(message_text) LIKE '%1-2 years%' OR
                LOWER(message_text) LIKE '%1-3 years%' OR
                LOWER(message_text) LIKE '%0 to 1%' OR
                LOWER(message_text) LIKE '%0 to 3%' OR
                LOWER(message_text) LIKE '%1 to 2%' OR
                LOWER(message_text) LIKE '%1 to 3%' OR
                LOWER(message_text) LIKE '%no experience%' OR
                LOWER(message_text) LIKE '%new graduate%' OR
                LOWER(message_text) LIKE '%recent graduate%' OR
                LOWER(message_text) LIKE '%fresh graduate%' OR
                LOWER(message_text) LIKE '%freshers welcome%' OR
                LOWER(message_text) LIKE '%beginners welcome%' OR
                LOWER(message_text) LIKE '%training provided%' OR
                LOWER(message_text) LIKE '%mentorship%' OR
                LOWER(message_text) LIKE '%entry position%'
            ) THEN 1 END) as fresher,
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
            'fresher': row['fresher'],
            'total': row['tech'] + row['non_tech'] + row['freelance'] + row['fresher']
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
        """)
    elif job_type == 'fresher':
        # Enhanced fresher job detection with comprehensive keywords
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
            WHERE (
                job_type LIKE '%fresher%' OR
                job_type LIKE '%entry%' OR
                job_type LIKE '%graduate%' OR
                job_type LIKE '%trainee%' OR
                job_type LIKE '%junior%' OR
                job_type LIKE '%intern%' OR
                job_type LIKE '%0-1%' OR
                job_type LIKE '%0-3%' OR
                job_type LIKE '%1-2%' OR
                job_type LIKE '%1-3%' OR
                LOWER(message_text) LIKE '%fresher%' OR
                LOWER(message_text) LIKE '%entry level%' OR
                LOWER(message_text) LIKE '%entry-level%' OR
                LOWER(message_text) LIKE '%graduate%' OR
                LOWER(message_text) LIKE '%trainee%' OR
                LOWER(message_text) LIKE '%junior%' OR
                LOWER(message_text) LIKE '%intern%' OR
                LOWER(message_text) LIKE '%0-1 years%' OR
                LOWER(message_text) LIKE '%0-3 years%' OR
                LOWER(message_text) LIKE '%1-2 years%' OR
                LOWER(message_text) LIKE '%1-3 years%' OR
                LOWER(message_text) LIKE '%0 to 1%' OR
                LOWER(message_text) LIKE '%0 to 3%' OR
                LOWER(message_text) LIKE '%1 to 2%' OR
                LOWER(message_text) LIKE '%1 to 3%' OR
                LOWER(message_text) LIKE '%no experience%' OR
                LOWER(message_text) LIKE '%new graduate%' OR
                LOWER(message_text) LIKE '%recent graduate%' OR
                LOWER(message_text) LIKE '%fresh graduate%' OR
                LOWER(message_text) LIKE '%freshers welcome%' OR
                LOWER(message_text) LIKE '%beginners welcome%' OR
                LOWER(message_text) LIKE '%training provided%' OR
                LOWER(message_text) LIKE '%mentorship%' OR
                LOWER(message_text) LIKE '%entry position%'
            )
            ORDER BY date DESC
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

@app.route('/api/available_dates')
def get_available_dates():
    """Get list of dates that have messages"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT DATE(date) as date, COUNT(*) as count
        FROM messages
        WHERE date IS NOT NULL
        GROUP BY DATE(date)
        ORDER BY date DESC
        LIMIT 60
    """)
    
    dates = []
    for row in cursor.fetchall():
        dates.append({
            'date': row['date'],
            'count': row['count']
        })
    
    conn.close()
    return jsonify(dates)

@app.route('/api/fresher_analysis')
def get_fresher_analysis():
    """Get detailed analysis of fresher/entry-level jobs with experience breakdown"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get fresher jobs with experience level categorization
    cursor.execute("""
        SELECT 
            message_text,
            job_type,
            keywords_found,
            date,
            group_name,
            sender,
            account_used,
            CASE 
                WHEN LOWER(message_text) LIKE '%0-1 years%' OR LOWER(message_text) LIKE '%0 to 1%' OR 
                     LOWER(message_text) LIKE '%no experience%' OR LOWER(message_text) LIKE '%fresher%' OR
                     LOWER(message_text) LIKE '%new graduate%' OR LOWER(message_text) LIKE '%recent graduate%' OR
                     LOWER(message_text) LIKE '%fresh graduate%' THEN '0-1 Years'
                WHEN LOWER(message_text) LIKE '%1-2 years%' OR LOWER(message_text) LIKE '%1 to 2%' OR
                     LOWER(message_text) LIKE '%junior%' THEN '1-2 Years'
                WHEN LOWER(message_text) LIKE '%0-3 years%' OR LOWER(message_text) LIKE '%0 to 3%' OR
                     LOWER(message_text) LIKE '%1-3 years%' OR LOWER(message_text) LIKE '%1 to 3%' OR
                     LOWER(message_text) LIKE '%entry level%' OR LOWER(message_text) LIKE '%entry-level%' OR
                     LOWER(message_text) LIKE '%entry position%' THEN '0-3 Years'
                WHEN LOWER(message_text) LIKE '%trainee%' OR LOWER(message_text) LIKE '%training provided%' OR
                     LOWER(message_text) LIKE '%mentorship%' THEN 'Trainee/Internship'
                WHEN LOWER(message_text) LIKE '%graduate%' OR LOWER(message_text) LIKE '%intern%' THEN 'Graduate/Intern'
                WHEN LOWER(message_text) LIKE '%beginners welcome%' OR LOWER(message_text) LIKE '%freshers welcome%' THEN 'Beginners Welcome'
                ELSE 'General Entry Level'
            END as experience_level
        FROM messages
        WHERE (
            job_type LIKE '%fresher%' OR
            job_type LIKE '%entry%' OR
            job_type LIKE '%graduate%' OR
            job_type LIKE '%trainee%' OR
            job_type LIKE '%junior%' OR
            job_type LIKE '%intern%' OR
            job_type LIKE '%0-1%' OR
            job_type LIKE '%0-3%' OR
            job_type LIKE '%1-2%' OR
            job_type LIKE '%1-3%' OR
            LOWER(message_text) LIKE '%fresher%' OR
            LOWER(message_text) LIKE '%entry level%' OR
            LOWER(message_text) LIKE '%entry-level%' OR
            LOWER(message_text) LIKE '%graduate%' OR
            LOWER(message_text) LIKE '%trainee%' OR
            LOWER(message_text) LIKE '%junior%' OR
            LOWER(message_text) LIKE '%intern%' OR
            LOWER(message_text) LIKE '%0-1 years%' OR
            LOWER(message_text) LIKE '%0-3 years%' OR
            LOWER(message_text) LIKE '%1-2 years%' OR
            LOWER(message_text) LIKE '%1-3 years%' OR
            LOWER(message_text) LIKE '%0 to 1%' OR
            LOWER(message_text) LIKE '%0 to 3%' OR
            LOWER(message_text) LIKE '%1 to 2%' OR
            LOWER(message_text) LIKE '%1 to 3%' OR
            LOWER(message_text) LIKE '%no experience%' OR
            LOWER(message_text) LIKE '%new graduate%' OR
            LOWER(message_text) LIKE '%recent graduate%' OR
            LOWER(message_text) LIKE '%fresh graduate%' OR
            LOWER(message_text) LIKE '%freshers welcome%' OR
            LOWER(message_text) LIKE '%beginners welcome%' OR
            LOWER(message_text) LIKE '%training provided%' OR
            LOWER(message_text) LIKE '%mentorship%' OR
            LOWER(message_text) LIKE '%entry position%'
        )
        ORDER BY date DESC
        LIMIT 500
    """)
    
    fresher_jobs = []
    experience_counts = {}
    
    for row in cursor.fetchall():
        experience_level = row['experience_level']
        if experience_level not in experience_counts:
            experience_counts[experience_level] = 0
        experience_counts[experience_level] += 1
        
        fresher_jobs.append({
            'text': row['message_text'],
            'company': 'Company Not Specified',
            'skills': row['keywords_found'],
            'salary': '',
            'work_mode': '',
            'score': 0,
            'date': row['date'],
            'group': row['group_name'],
            'job_type': row['job_type'],
            'experience_level': experience_level
        })
    
    conn.close()
    
    return jsonify({
        'fresher_jobs': fresher_jobs,
        'experience_breakdown': experience_counts,
        'total_fresher_jobs': len(fresher_jobs)
    })

@app.route('/api/messages_by_date/<date>/<job_type>')
def get_messages_by_date(date, job_type):
    """Get messages by date and job type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query based on job type
    if job_type == 'all':
        query = """
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE DATE(date) = ?
            ORDER BY date DESC
        """
    elif job_type == 'tech':
        query = """
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE DATE(date) = ? 
            AND job_type LIKE '%tech%' 
            AND job_type NOT LIKE '%non_tech%'
            ORDER BY date DESC
        """
    elif job_type == 'non_tech':
        query = """
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE DATE(date) = ? 
            AND job_type = 'non_tech'
            ORDER BY date DESC
        """
    elif job_type == 'freelance':
        query = """
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE DATE(date) = ? 
            AND job_type LIKE '%freelance%'
            ORDER BY date DESC
        """
    elif job_type == 'fresher':
        # Enhanced fresher job detection for date-wise filtering
        query = """
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE DATE(date) = ? 
            AND (
                job_type LIKE '%fresher%' OR
                job_type LIKE '%entry%' OR
                job_type LIKE '%graduate%' OR
                job_type LIKE '%trainee%' OR
                job_type LIKE '%junior%' OR
                job_type LIKE '%intern%' OR
                job_type LIKE '%0-1%' OR
                job_type LIKE '%0-3%' OR
                job_type LIKE '%1-2%' OR
                job_type LIKE '%1-3%' OR
                LOWER(message_text) LIKE '%fresher%' OR
                LOWER(message_text) LIKE '%entry level%' OR
                LOWER(message_text) LIKE '%entry-level%' OR
                LOWER(message_text) LIKE '%graduate%' OR
                LOWER(message_text) LIKE '%trainee%' OR
                LOWER(message_text) LIKE '%junior%' OR
                LOWER(message_text) LIKE '%intern%' OR
                LOWER(message_text) LIKE '%0-1 years%' OR
                LOWER(message_text) LIKE '%0-3 years%' OR
                LOWER(message_text) LIKE '%1-2 years%' OR
                LOWER(message_text) LIKE '%1-3 years%' OR
                LOWER(message_text) LIKE '%0 to 1%' OR
                LOWER(message_text) LIKE '%0 to 3%' OR
                LOWER(message_text) LIKE '%1 to 2%' OR
                LOWER(message_text) LIKE '%1 to 3%' OR
                LOWER(message_text) LIKE '%no experience%' OR
                LOWER(message_text) LIKE '%new graduate%' OR
                LOWER(message_text) LIKE '%recent graduate%' OR
                LOWER(message_text) LIKE '%fresh graduate%' OR
                LOWER(message_text) LIKE '%freshers welcome%' OR
                LOWER(message_text) LIKE '%beginners welcome%' OR
                LOWER(message_text) LIKE '%training provided%' OR
                LOWER(message_text) LIKE '%mentorship%' OR
                LOWER(message_text) LIKE '%entry position%'
            )
            ORDER BY date DESC
        """
    else:
        query = """
            SELECT 
                message_text,
                job_type,
                keywords_found,
                date,
                group_name,
                sender,
                account_used
            FROM messages
            WHERE DATE(date) = ?
            ORDER BY date DESC
        """
    
    cursor.execute(query, (date,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'text': row['message_text'],
            'company': 'Company Not Specified',
            'skills': row['keywords_found'],
            'salary': '',
            'work_mode': '',
            'score': 0,
            'date': row['date'],
            'group': row['group_name'],
            'job_type': row['job_type']
        })
    
    conn.close()
    return jsonify(messages)

if __name__ == '__main__':
    print("="*60)
    print("🌐 Starting Web Dashboard")
    print("="*60)
    print()
    print("Dashboard will open at: http://localhost:7001")
    print()
    print("Press Ctrl+C to stop")
    print("="*60)
    print()
    
    # Allow overriding port via environment variable for flexibility
    port = int(os.getenv('DASHBOARD_PORT', os.getenv('PORT', '7001')))
    app.run(debug=True, host='0.0.0.0', port=port)

