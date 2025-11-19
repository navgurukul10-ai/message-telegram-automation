"""
Quick Test Mode - First time testing के लिए
Faster rate limits for immediate results
"""
import asyncio
import sys
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import FloodWaitError

from config import ACCOUNTS, MESSAGE_YEAR_FILTER, PATHS
from utils.logger import get_logger
from utils.database import DatabaseHandler
from utils.classifier import MessageClassifier
from utils.csv_handler import CSVHandler
from utils.job_verifier import JobVerifier

logger = get_logger('quick_test')

async def quick_test():
    """Quick test with 3 groups only"""
    
    print("\n" + "="*70)
    print("  🧪 QUICK TEST MODE - First Time Testing")
    print("="*70)
    print()
    print("  This will:")
    print("  ✅ Join 3 groups quickly (10 second delays)")
    print("  ✅ Fetch 20 messages per group")
    print("  ✅ Show you how it works")
    print("  ✅ Save to database & CSV")
    print()
    print("  Time needed: ~5-10 minutes")
    print("="*70)
    print()
    
    input("Press Enter to start test... ")
    
    # Initialize
    db = DatabaseHandler()
    classifier = MessageClassifier()
    csv_handler = CSVHandler()
    job_verifier = JobVerifier()
    
    # Load groups
    with open(PATHS['groups_json'], 'r', encoding='utf-8') as f:
        all_groups = json.load(f)
    
    # Take first 3 groups
    test_groups = all_groups[:3]
    
    print(f"\n📋 Will test with these 3 groups:")
    for i, g in enumerate(test_groups, 1):
        print(f"  {i}. {g['name']} - {g['link']}")
    print()
    
    # Use first account
    account = ACCOUNTS[0]
    session_path = f"{PATHS['sessions']}{account['session_name']}"
    
    client = TelegramClient(session_path, account['api_id'], account['api_hash'])
    await client.connect()
    
    logger.info(f"Using account: {account['name']}")
    
    total_jobs = 0
    
    for i, group in enumerate(test_groups, 1):
        try:
            print(f"\n{'='*70}")
            print(f"  Processing Group {i}/3: {group['name']}")
            print(f"{'='*70}")
            
            group_link = group['link']
            
            # Extract username
            if 'joinchat' in group_link or '+' in group_link:
                print(f"  ⏳ Joining private group...")
                entity = await client.get_entity(group_link)
            else:
                username = group_link.split('/')[-1]
                print(f"  ⏳ Joining @{username}...")
                try:
                    entity = await client.get_entity(username)
                except:
                    print(f"  ❌ Could not access group. Skipping...")
                    continue
            
            group_name = entity.title if hasattr(entity, 'title') else username
            print(f"  ✅ Accessed: {group_name}")
            
            # Fetch messages
            print(f"  📥 Fetching messages...")
            
            message_count = 0
            job_count = 0
            
            async for message in client.iter_messages(entity, limit=20):
                message_count += 1
                
                if not message.text:
                    continue
                
                # Check year
                if message.date.year != MESSAGE_YEAR_FILTER:
                    continue
                
                # Classify
                job_type, keywords = classifier.classify(message.text)
                
                if not job_type:
                    continue
                
                # Verify and extract
                verification = job_verifier.verify_and_extract(message.text)
                
                # Prepare data
                message_data = {
                    'message_id': f"{entity.id}_{message.id}",
                    'group_name': group_name,
                    'group_link': group_link,
                    'sender': str(message.sender_id) if message.sender_id else 'Unknown',
                    'date': message.date.isoformat(),
                    'message_text': message.text,
                    'job_type': job_type,
                    'keywords_found': ','.join(keywords),
                    'account_used': account['name']
                }
                
                if verification:
                    message_data.update(verification)
                
                # Save
                db.insert_message(message_data)
                csv_handler.write_message(message_data)
                
                job_count += 1
                total_jobs += 1
                
                print(f"     ✅ Job #{job_count}: {job_type} - {verification.get('company_name', 'N/A')[:30]}")
            
            print(f"  📊 Found {job_count} jobs from {message_count} messages")
            
            # Save group info
            db.insert_group({
                'group_name': group_name,
                'group_link': group_link,
                'join_date': datetime.now(),
                'account_used': account['name'],
                'messages_fetched': message_count
            })
            
            # Small delay before next group
            if i < len(test_groups):
                print(f"  ⏳ Waiting 10 seconds before next group...")
                await asyncio.sleep(10)
        
        except FloodWaitError as e:
            print(f"  ⚠️  FloodWait: Need to wait {e.seconds} seconds")
            print(f"     This is normal, system is being safe!")
            await asyncio.sleep(e.seconds)
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            logger.error(f"Error processing {group.get('name')}: {e}")
            continue
    
    await client.disconnect()
    
    print("\n" + "="*70)
    print("  ✅ QUICK TEST COMPLETE!")
    print("="*70)
    print()
    print(f"  📊 Results:")
    print(f"     Groups Processed: {len(test_groups)}")
    print(f"     Jobs Found: {total_jobs}")
    print()
    print("  💾 Data saved to:")
    print("     ✅ Database: data/database/telegram_jobs.db")
    print("     ✅ CSV: data/csv/*.csv")
    print()
    print("  🔍 Check results:")
    print("     python3 check_status.py")
    print()
    print("  🌐 View in browser:")
    print("     python3 web_dashboard.py")
    print("     Then open: http://localhost:7000")
    print()
    print("="*70)
    print()

if __name__ == "__main__":
    asyncio.run(quick_test())

