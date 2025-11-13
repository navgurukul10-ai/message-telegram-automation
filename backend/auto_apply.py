#!/usr/bin/env python3
"""
Auto Apply Script - Automatically apply to filtered jobs
For Gaurav Rajput (DevOps Engineer)
"""
import sys
import os
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.auto_apply.link_extractor import LinkExtractor
from src.auto_apply.job_filter import JobFilter
from src.auto_apply.email_sender import EmailApplicationSender
from src.auto_apply.tracker import ApplicationTracker
from src.utils.logger import get_logger

logger = get_logger('auto_apply')


def main():
    parser = argparse.ArgumentParser(description='Auto Apply to Jobs')
    parser.add_argument('--profile', default='config/gaurav_profile.json', 
                       help='Path to user profile JSON')
    parser.add_argument('--days', type=int, default=7, 
                       help='Look for jobs from last N days')
    parser.add_argument('--job-type', default='tech', 
                       help='Job type: tech, freelance_tech, or all')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Dry run - don\'t actually send emails')
    parser.add_argument('--max-applications', type=int, default=10, 
                       help='Maximum applications to send')
    parser.add_argument('--min-match-score', type=float, default=30.0, 
                       help='Minimum skill match score percentage')
    parser.add_argument('--email-only', action='store_true', 
                       help='Only apply to jobs with email applications')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  🤖 AUTO APPLY SYSTEM")
    print("="*70)
    print()
    
    # Initialize components
    logger.info("Initializing Auto Apply System...")
    
    link_extractor = LinkExtractor()
    job_filter = JobFilter(args.profile)
    email_sender = EmailApplicationSender(args.profile)
    tracker = ApplicationTracker()
    
    # Get application stats
    stats = tracker.get_stats()
    print(f"📊 Application Stats:")
    print(f"   • Total applications: {stats['total']}")
    print(f"   • Applications today: {stats['today']}")
    print()
    
    # Check daily limit
    if stats['today'] >= args.max_applications:
        print(f"⚠️  Daily limit reached ({stats['today']}/{args.max_applications})")
        print("   Run again tomorrow!")
        return
    
    # Step 1: Extract applicable jobs
    print(f"🔍 Step 1: Extracting jobs from last {args.days} days...")
    applicable_jobs = link_extractor.get_applicable_jobs(args.job_type, args.days)
    
    if not applicable_jobs:
        print("   No applicable jobs found!")
        return
    
    print(f"   Found {len(applicable_jobs)} applicable jobs")
    print()
    
    # Categorize by type
    categorized = link_extractor.categorize_by_type(applicable_jobs)
    
    print("📋 Jobs by Application Type:")
    for app_type, jobs in categorized.items():
        if jobs:
            print(f"   • {app_type}: {len(jobs)} jobs")
    print()
    
    # Step 2: Filter jobs based on profile
    print(f"🎯 Step 2: Filtering jobs (min match score: {args.min_match_score}%)...")
    filtered_jobs = job_filter.filter_jobs(applicable_jobs, args.min_match_score)
    
    if not filtered_jobs:
        print("   No jobs match your profile!")
        return
    
    print(f"   {len(filtered_jobs)} jobs match your profile")
    # Extra visibility: how many of the filtered jobs are email-based
    filtered_email_jobs = [j for j in filtered_jobs if j.get('application_type') == 'email']
    if filtered_email_jobs:
        print(f"   • Email-ready jobs in filtered set: {len(filtered_email_jobs)}")
    else:
        print("   • Email-ready jobs in filtered set: 0")
    
    # Prioritize email jobs by moving them to the front
    email_jobs = [j for j in filtered_jobs if j.get('application_type') == 'email']
    non_email_jobs = [j for j in filtered_jobs if j.get('application_type') != 'email']
    filtered_jobs = email_jobs + non_email_jobs
    print()
    
    # Step 3: Apply to jobs
    print(f"📧 Step 3: Applying to jobs...")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()
    
    applications_sent = 0
    remaining_quota = args.max_applications - stats['today']
    
    for i, job in enumerate(filtered_jobs):
        if applications_sent >= remaining_quota:
            print(f"\n⚠️  Reached daily limit ({args.max_applications} applications)")
            break
        
        # Skip if already applied
        if tracker.is_already_applied(job['message_id']):
            logger.debug(f"Already applied to job {job['message_id']}")
            continue
        
        # Filter for email-only if requested
        if args.email_only and job['application_type'] != 'email':
            continue
        
        # Apply based on type
        if job['application_type'] == 'email':
            print(f"\n📧 Job {i+1}: {job['message_text'].split(chr(10))[0][:60]}...")
            print(f"   Group: {job['group_name']}")
            print(f"   Match Score: {job.get('match_score', 0):.1f}%")
            print(f"   Email: {job['application_link']}")
            
            # Send application
            result = email_sender.send_application(
                job['application_link'], 
                job, 
                dry_run=args.dry_run
            )
            
            if result['status'] in ['sent', 'dry_run']:
                print(f"   ✅ Application {'would be ' if args.dry_run else ''}sent!")
                if result.get('cc'):
                    print(f"   📋 CC: {result['cc']}")
                
                # Track application
                if not args.dry_run:
                    tracker.record_application(job, 'sent')
                    applications_sent += 1
                    
                    # Delay between applications
                    if applications_sent < remaining_quota:
                        delay = 10  # 10 seconds between emails
                        print(f"   ⏳ Waiting {delay} seconds...")
                        time.sleep(delay)
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                if not args.dry_run:
                    tracker.record_application(job, 'failed')
        
        elif job['application_type'] == 'linkedin':
            print(f"\n🔗 Job {i+1}: LinkedIn (Manual action required)")
            print(f"   Link: {job['application_link']}")
            print(f"   Match Score: {job.get('match_score', 0):.1f}%")
            print(f"   ℹ️  LinkedIn applications require manual submission")
        
        else:
            print(f"\n🌐 Job {i+1}: {job['application_type']} (Manual action required)")
            print(f"   Link: {job['application_link']}")
            print(f"   Match Score: {job.get('match_score', 0):.1f}%")
    
    print()
    print("="*70)
    print("  ✅ AUTO APPLY COMPLETE")
    print("="*70)
    print()
    print(f"📊 Summary:")
    print(f"   • Applications sent: {applications_sent}")
    print(f"   • Total today: {stats['today'] + applications_sent}")
    print(f"   • Remaining quota: {remaining_quota - applications_sent}")
    print()
    
    if args.dry_run:
        print("💡 This was a DRY RUN. Run without --dry-run to actually send emails.")
    else:
        if applications_sent > 0:
            print("💡 Check your email for sent applications!")
            if email_sender.cc_emails:
                print(f"   CC sent to: {', '.join(email_sender.cc_emails)}")
        else:
            print("💡 No email applications were sent in this run (filtered jobs may be non-email).")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


