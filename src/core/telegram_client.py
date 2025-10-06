"""
Telegram client with safety features and rate limiting
"""
import asyncio
import random
import json
import os
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError, ChannelPrivateError, UserBannedInChannelError,
    ChatWriteForbiddenError, ChannelInvalidError
)
from telethon.tl.types import Channel, Chat
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from config.settings import ACCOUNTS, RATE_LIMITS, MESSAGE_YEAR_FILTER, PATHS
from src.utils.logger import get_logger
from src.storage.database import DatabaseHandler
from src.services.classifier import MessageClassifier
from src.storage.csv_handler import CSVHandler
from src.services.job_verifier import JobVerifier

logger = get_logger('telegram_client')

class TelegramJobFetcher:
    """Main Telegram client with safety features"""
    
    def __init__(self):
        self.accounts = ACCOUNTS
        self.clients = []
        self.current_account_index = 0
        self.db = DatabaseHandler()
        self.classifier = MessageClassifier()
        self.csv_handler = CSVHandler()
        self.job_verifier = JobVerifier()
        
        # Create sessions directory
        os.makedirs(PATHS['sessions'], exist_ok=True)
        os.makedirs(PATHS['json'], exist_ok=True)
        
        # Load tracking data
        self.processed_messages = set()
        self.joined_groups = {}
        self._load_tracking_data()
    
    def _load_tracking_data(self):
        """Load processed messages and joined groups"""
        # Load from database
        self.processed_messages = set(self.db.get_processed_message_ids())
        
        joined = self.db.get_joined_groups()
        for group in joined:
            self.joined_groups[group['group_link']] = {
                'name': group['group_name'],
                'account': group['account_used']
            }
        
        logger.info(f"Loaded {len(self.processed_messages)} processed messages")
        logger.info(f"Loaded {len(self.joined_groups)} joined groups")
    
    async def initialize_clients(self):
        """Initialize Telegram clients for all accounts"""
        logger.info("Initializing Telegram clients...")
        
        for account in self.accounts:
            try:
                session_path = os.path.join(PATHS['sessions'], account['session_name'])
                
                client = TelegramClient(
                    session_path,
                    account['api_id'],
                    account['api_hash']
                )
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    logger.warning(f"Account {account['name']} needs authorization")
                    await client.send_code_request(account['phone'])
                    logger.info(f"Code sent to {account['phone']}. Please check your Telegram app.")
                    
                    # Wait for user to enter code
                    code = input(f"Enter the code for {account['name']} ({account['phone']}): ")
                    await client.sign_in(account['phone'], code)
                    
                    logger.info(f"Account {account['name']} authorized successfully")
                else:
                    logger.info(f"Account {account['name']} already authorized")
                
                self.clients.append({
                    'client': client,
                    'account': account,
                    'last_action': None,
                    'groups_joined_today': 0,
                    'messages_fetched_today': 0
                })
            
            except Exception as e:
                logger.error(f"Failed to initialize {account['name']}: {e}")
        
        logger.info(f"Initialized {len(self.clients)} clients successfully")
    
    def _get_next_client(self):
        """Get next available client with rotation"""
        # Check account usage limits
        for _ in range(len(self.clients)):
            client_info = self.clients[self.current_account_index]
            
            # Get today's usage from database
            usage = self.db.get_account_usage_today(client_info['account']['name'])
            
            # Check if account has reached daily limits
            if usage['groups_joined'] < RATE_LIMITS['max_groups_per_day']:
                selected_client = client_info
                self.current_account_index = (self.current_account_index + 1) % len(self.clients)
                return selected_client
            
            # Try next account
            self.current_account_index = (self.current_account_index + 1) % len(self.clients)
        
        # All accounts exhausted
        logger.warning("All accounts have reached daily limits")
        return None
    
    async def _safe_delay(self, delay_range):
        """Add random delay for human-like behavior"""
        delay = random.uniform(delay_range[0], delay_range[1])
        logger.debug(f"Waiting {delay:.2f} seconds...")
        await asyncio.sleep(delay)
    
    def _is_working_hours(self):
        """Check if current time is within working hours"""
        current_hour = datetime.now().hour
        start_hour, end_hour = RATE_LIMITS.get('working_hours', (0, 24))
        
        if current_hour < start_hour or current_hour >= end_hour:
            logger.info(f"Outside working hours ({start_hour}-{end_hour}). Current: {current_hour}")
            return False
        return True
    
    async def join_group(self, group_link, client_info):
        """Safely join a Telegram group"""
        try:
            # Check if already joined
            if group_link in self.joined_groups:
                logger.info(f"Group {group_link} already joined")
                return True
            
            # Add delay before joining
            await self._safe_delay(RATE_LIMITS['join_group_delay'])
            
            client = client_info['client']
            account = client_info['account']
            
            # Extract username from link and join
            if 'joinchat' in group_link or '+' in group_link:
                # Private group with invite link
                # Extract hash from link
                invite_hash = group_link.split('/')[-1].replace('+', '')
                result = await client(ImportChatInviteRequest(invite_hash))
                entity = result.chats[0] if result.chats else None
                if not entity:
                    raise Exception("Could not join private group")
            else:
                # Public group
                username = group_link.split('/')[-1]
                entity = await client.get_entity(username)
                # Join the channel/group
                if isinstance(entity, Channel):
                    await client(JoinChannelRequest(entity))
                # For Chat type, we're already in after get_entity
            
            group_name = entity.title if hasattr(entity, 'title') else username
            
            # Update tracking
            self.joined_groups[group_link] = {
                'name': group_name,
                'account': account['name'],
                'join_date': datetime.now().isoformat()
            }
            
            # Save to database
            self.db.insert_group({
                'group_name': group_name,
                'group_link': group_link,
                'join_date': datetime.now(),
                'account_used': account['name']
            })
            
            # Save to CSV
            self.csv_handler.write_group({
                'group_name': group_name,
                'group_link': group_link,
                'join_date': datetime.now().isoformat(),
                'account_used': account['name'],
                'messages_fetched': 0,
                'last_message_date': ''
            })
            
            # Update account usage
            self.db.update_account_usage(account['name'], groups_joined=1)
            
            logger.info(f"Successfully joined group: {group_name} using {account['name']}")
            return True
        
        except FloodWaitError as e:
            logger.warning(f"FloodWait error: need to wait {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return False
        
        except (ChannelPrivateError, UserBannedInChannelError, ChannelInvalidError) as e:
            logger.error(f"Cannot join group {group_link}: {e}")
            return False
        
        except Exception as e:
            logger.error(f"Error joining group {group_link}: {e}")
            return False
    
    async def fetch_messages(self, group_link, client_info, limit=None):
        """Fetch messages from a group"""
        try:
            # Use safe limit from config
            if limit is None:
                limit = RATE_LIMITS.get('daily_message_limit', 75)
            
            client = client_info['client']
            account = client_info['account']
            
            # Get entity
            if 'joinchat' in group_link or '+' in group_link:
                entity = await client.get_entity(group_link)
            else:
                username = group_link.split('/')[-1]
                entity = await client.get_entity(username)
            
            group_name = entity.title if hasattr(entity, 'title') else username
            
            # Fetch messages
            messages = []
            new_messages_count = 0
            
            async for message in client.iter_messages(entity, limit=limit):
                # Add small delay between fetches
                await self._safe_delay(RATE_LIMITS['message_fetch_delay'])
                
                # Skip if no text
                if not message.text:
                    continue
                
                # Check if message is from current year
                if message.date.year != MESSAGE_YEAR_FILTER:
                    continue
                
                # Create unique message ID
                message_id = f"{entity.id}_{message.id}"
                
                # Skip if already processed
                if message_id in self.processed_messages:
                    continue
                
                # Classify message
                job_type, keywords = self.classifier.classify(message.text)
                
                # Skip if not a job message
                if not job_type:
                    continue
                
                # Verify job and extract company info
                verification_result = self.job_verifier.verify_and_extract(message.text)
                
                # Prepare message data with enhanced fields
                message_data = {
                    'message_id': message_id,
                    'group_name': group_name,
                    'group_link': group_link,
                    'sender': message.sender_id if message.sender_id else 'Unknown',
                    'date': message.date.isoformat(),
                    'message_text': message.text,
                    'job_type': job_type,
                    'keywords_found': ','.join(keywords),
                    'account_used': account['name']
                }
                
                # Add verification and company info if available
                if verification_result:
                    message_data.update(verification_result)
                    logger.debug(f"Job verified: {verification_result['is_verified']}, "
                               f"Score: {verification_result['verification_score']:.2f}%, "
                               f"Company: {verification_result['company_name']}")
                
                # Save to database (will go to category-specific table too)
                self.db.insert_message(message_data)
                
                # Save to CSV
                self.csv_handler.write_message(message_data)
                
                # Update tracking
                self.processed_messages.add(message_id)
                messages.append(message_data)
                new_messages_count += 1
                
                logger.info(f"Fetched job message: {job_type} from {group_name}")
            
            # Update account usage
            if new_messages_count > 0:
                self.db.update_account_usage(account['name'], messages_fetched=new_messages_count)
            
            logger.info(f"Fetched {new_messages_count} new job messages from {group_name}")
            return messages
        
        except FloodWaitError as e:
            logger.warning(f"FloodWait error: need to wait {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return []
        
        except Exception as e:
            logger.error(f"Error fetching messages from {group_link}: {e}")
            return []
    
    async def process_groups(self, groups_data):
        """Process list of groups"""
        logger.info(f"Starting to process {len(groups_data)} groups...")
        
        for i, group in enumerate(groups_data):
            try:
                # Check if within working hours
                if not self._is_working_hours():
                    logger.info("Outside working hours. Pausing...")
                    await asyncio.sleep(1800)  # Wait 30 minutes
                    continue
                
                group_link = group.get('link')
                
                if not group_link:
                    continue
                
                # Get next available client
                client_info = self._get_next_client()
                
                if not client_info:
                    logger.warning("No available clients. Waiting before retry...")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    client_info = self._get_next_client()
                    if not client_info:
                        logger.error("Still no available clients. Stopping...")
                        break
                
                # Join group if not already joined
                if group_link not in self.joined_groups:
                    success = await self.join_group(group_link, client_info)
                    if not success:
                        continue
                
                # Fetch messages
                messages = await self.fetch_messages(group_link, client_info)
                
                logger.info(f"Processed {i+1}/{len(groups_data)} groups")
                
            except Exception as e:
                logger.error(f"Error processing group {group.get('name', 'Unknown')}: {e}")
                continue
    
    async def run_continuous(self, duration_days=30):
        """Run the fetcher continuously for specified days"""
        logger.info(f"Starting continuous run for {duration_days} days...")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(days=duration_days)
        
        # Load groups data
        with open(PATHS['groups_json'], 'r', encoding='utf-8') as f:
            groups_data = json.load(f)
        
        logger.info(f"Loaded {len(groups_data)} groups from data.json")
        
        check_interval = RATE_LIMITS.get('check_interval', 3600)
        
        while datetime.now() < end_time:
            try:
                logger.info("Starting new fetch cycle...")
                
                # Process all groups
                await self.process_groups(groups_data)
                
                # Wait before next cycle
                logger.info(f"Fetch cycle complete. Waiting {check_interval} seconds before next cycle...")
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in continuous run: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
        
        logger.info("Continuous run completed!")
    
    async def close_clients(self):
        """Close all client connections"""
        for client_info in self.clients:
            await client_info['client'].disconnect()
        logger.info("All clients disconnected")

