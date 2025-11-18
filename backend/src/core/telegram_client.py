"""
Telegram client with safety features and rate limiting
"""
import asyncio
import random
import json
import os
import sqlite3
from datetime import datetime, timedelta

# IMPORTANT: Patch Telethon sessions before importing TelegramClient
from src.utils.telethon_session_fix import patch_telethon_sessions
patch_telethon_sessions()

from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError, ChannelPrivateError, UserBannedInChannelError,
    ChatWriteForbiddenError, ChannelInvalidError, AuthKeyError,
    TimeoutError as TelethonTimeoutError, ServerError, RpcCallFailError
)
from telethon.tl.types import Channel, Chat
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
import signal
import sys

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
        self.is_shutting_down = False
        self._running_tasks = []
        self._db_write_lock = asyncio.Lock()
        self._last_db_write = 0
        
        # Create sessions directory
        os.makedirs(PATHS['sessions'], exist_ok=True)
        os.makedirs(PATHS['json'], exist_ok=True)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Load tracking data
        self.processed_messages = set()
        self.joined_groups = {}
        self._load_tracking_data()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.is_shutting_down = True
    
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
        """Initialize Telegram clients for all accounts with robust error handling"""
        logger.info("Initializing Telegram clients...")
        
        for idx, account in enumerate(self.accounts):
            # Add delay between client initializations to prevent session file conflicts
            if idx > 0:
                delay = 3  # 3 seconds between each client
                logger.info(f"Waiting {delay}s before initializing next client...")
                await asyncio.sleep(delay)
            max_retries = 5  # Increased retries
            retry_delay = 10
            client = None
            
            for attempt in range(max_retries):
                try:
                    session_path = os.path.join(PATHS['sessions'], account['session_name'])
                    
                    # Check network connectivity first
                    if attempt == 0:
                        try:
                            import socket
                            socket.create_connection(("8.8.8.8", 53), timeout=5)
                        except OSError:
                            logger.warning("⚠️  No internet connection detected. Waiting 10 seconds...")
                            await asyncio.sleep(10)
                            continue
                    
                    # Create client with optimized timeout settings
                    client = TelegramClient(
                        session_path,
                        account['api_id'],
                        account['api_hash'],
                        connection_retries=3,  # Reduced internal retries, we handle retries externally
                        retry_delay=3,
                        timeout=120,  # Increased timeout to 120 seconds for slow networks
                        request_retries=3,
                        auto_reconnect=False,  # Disable auto-reconnect to avoid AttributeError issues
                        flood_sleep_threshold=0  # Handle flood waits manually
                    )
                    
                    # Try to connect with timeout handling
                    logger.info(f"Connecting {account['name']} (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.wait_for(client.connect(), timeout=150)  # Increased to 150 seconds
                    
                    # Verify connection is healthy
                    if not await client.is_user_authorized():
                        logger.warning(f"Account {account['name']} needs authorization")
                        await client.send_code_request(account['phone'])
                        logger.info(f"Code sent to {account['phone']}. Please check your Telegram app.")
                        
                        # Wait for user to enter code
                        code = input(f"Enter the code for {account['name']} ({account['phone']}): ")
                        await client.sign_in(account['phone'], code)
                        
                        logger.info(f"Account {account['name']} authorized successfully")
                    else:
                        # Test connection with a simple API call
                        me = await asyncio.wait_for(client.get_me(), timeout=30)
                        logger.info(f"Account {account['name']} already authorized ({me.first_name})")
                    
                    self.clients.append({
                        'client': client,
                        'account': account,
                        'last_action': None,
                        'groups_joined_today': 0,
                        'messages_fetched_today': 0,
                        'reconnect_attempts': 0
                    })
                    
                    # Success! Break the retry loop
                    logger.info(f"✅ Successfully initialized {account['name']}")
                    break
                
                except asyncio.TimeoutError:
                    logger.warning(f"⏱️  Timeout connecting {account['name']} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 180)  # Cap at 3 minutes
                    else:
                        logger.error(f"❌ Failed to connect {account['name']} after {max_retries} attempts")
                        logger.error("💡 Possible causes: Slow internet, Telegram server issues, or firewall blocking")
                    
                    # Cleanup failed client
                    if client:
                        try:
                            if hasattr(client, 'disconnect'):
                                await asyncio.wait_for(client.disconnect(), timeout=10)
                        except Exception as cleanup_error:
                            logger.debug(f"Cleanup error (ignored): {cleanup_error}")
                        client = None
                
                except (ConnectionError, OSError, ServerError, RpcCallFailError, AttributeError) as e:
                    error_msg = str(e)
                    if 'NoneType' in error_msg or 'connect' in error_msg:
                        logger.warning(f"🔌 Telethon connection error for {account['name']}: {e}")
                    else:
                        logger.warning(f"🔌 Network error for {account['name']}: {e}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"Connection issue detected. Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 180)  # Cap at 3 minutes
                    else:
                        logger.error(f"❌ Network issues persist for {account['name']}. Skipping.")
                    
                    # Cleanup client properly
                    if client:
                        try:
                            if hasattr(client, 'disconnect'):
                                await asyncio.wait_for(client.disconnect(), timeout=10)
                        except Exception as cleanup_error:
                            logger.debug(f"Cleanup error (ignored): {cleanup_error}")
                        client = None
                
                except AuthKeyError as e:
                    logger.error(f"🔑 Auth key error for {account['name']}: {e}")
                    logger.error("Session file may be corrupted. You may need to re-authorize this account.")
                    break  # Don't retry auth key errors
                
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {account['name']}: {type(e).__name__}: {e}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 120)
                    else:
                        logger.error(f"Giving up on {account['name']} after {max_retries} attempts")
                    
                    if client:
                        try:
                            await asyncio.wait_for(client.disconnect(), timeout=10)
                        except:
                            pass
        
        logger.info(f"✅ Initialized {len(self.clients)} clients successfully out of {len(self.accounts)} accounts")
    
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
    
    async def _safe_db_write(self, write_func, *args, **kwargs):
        """Safely write to database with locking to prevent concurrent access"""
        max_retries = 10  # Increased retries for database locks
        retry_delay = 2
        
        for attempt in range(max_retries):
            async with self._db_write_lock:
                try:
                    # Add small delay between writes to prevent lock contention
                    current_time = asyncio.get_event_loop().time()
                    time_since_last_write = current_time - self._last_db_write
                    if time_since_last_write < 0.2:  # 200ms minimum between writes
                        await asyncio.sleep(0.2 - time_since_last_write)
                    
                    # Perform the write
                    result = write_func(*args, **kwargs)
                    self._last_db_write = asyncio.get_event_loop().time()
                    return result
                    
                except sqlite3.OperationalError as e:
                    if 'database is locked' in str(e) and attempt < max_retries - 1:
                        logger.warning(f"💾 Database locked in _safe_db_write (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 1.5, 15)  # Exponential backoff, max 15s
                        continue
                    else:
                        logger.error(f"Database error in _safe_db_write after {max_retries} attempts: {e}")
                        return False  # Return False instead of raising to allow graceful handling
                except Exception as e:
                    logger.error(f"Error in _safe_db_write: {e}")
                    return False  # Return False instead of raising to allow graceful handling
    
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
                result = await asyncio.wait_for(
                    client(ImportChatInviteRequest(invite_hash)), 
                    timeout=60
                )
                entity = result.chats[0] if result.chats else None
                if not entity:
                    raise Exception("Could not join private group")
            else:
                # Public group
                username = group_link.split('/')[-1]
                entity = await asyncio.wait_for(
                    client.get_entity(username),
                    timeout=60
                )
                # Join the channel/group
                if isinstance(entity, Channel):
                    await asyncio.wait_for(
                        client(JoinChannelRequest(entity)),
                        timeout=60
                    )
                # For Chat type, we're already in after get_entity
            
            group_name = entity.title if hasattr(entity, 'title') else username
            
            # Update tracking
            self.joined_groups[group_link] = {
                'name': group_name,
                'account': account['name'],
                'join_date': datetime.now().isoformat()
            }
            
            # Save to database with safe locking
            await self._safe_db_write(
                self.db.insert_group,
                {
                    'group_name': group_name,
                    'group_link': group_link,
                    'join_date': datetime.now(),
                    'account_used': account['name']
                }
            )
            
            # Save to CSV
            self.csv_handler.write_group({
                'group_name': group_name,
                'group_link': group_link,
                'join_date': datetime.now().isoformat(),
                'account_used': account['name'],
                'messages_fetched': 0,
                'last_message_date': ''
            })
            
            # Update account usage with safe locking
            await self._safe_db_write(
                self.db.update_account_usage,
                account['name'],
                groups_joined=1
            )
            
            logger.info(f"Successfully joined group: {group_name} using {account['name']}")
            return True
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout joining group {group_link}")
            return False
        
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
        """Fetch messages from a group with robust error handling"""
        max_retries = 5  # Increased from 3 to handle database locks better
        
        for retry in range(max_retries):
            try:
                # Check if shutting down
                if self.is_shutting_down:
                    logger.info("Shutdown requested, skipping message fetch")
                    return []
                
                # Use safe limit from config
                if limit is None:
                    limit = RATE_LIMITS.get('daily_message_limit', 75)
                
                client = client_info['client']
                account = client_info['account']
                
                # Get entity with timeout
                if 'joinchat' in group_link or '+' in group_link:
                    entity = await asyncio.wait_for(
                        client.get_entity(group_link),
                        timeout=60
                    )
                else:
                    username = group_link.split('/')[-1]
                    entity = await asyncio.wait_for(
                        client.get_entity(username),
                        timeout=60
                    )
                
                group_name = entity.title if hasattr(entity, 'title') else username
                
                # Fetch messages
                messages = []
                new_messages_count = 0
                messages_checked = 0
                consecutive_old = 0  # Track consecutive old/processed messages
                
                async for message in client.iter_messages(entity, limit=limit):
                    # Check shutdown flag
                    if self.is_shutting_down:
                        logger.info("Shutdown requested during message fetch")
                        break
                    
                    messages_checked += 1
                    
                    # Add small delay between fetches (but only if we're still finding new messages)
                    if messages_checked > 1:  # Skip delay for first message
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
                        consecutive_old += 1
                        # If we've seen 10 consecutive old messages, likely all are old - skip rest
                        if consecutive_old >= 10:
                            logger.debug(f"Found 10 consecutive old messages, skipping rest for {group_name}")
                            break
                        continue
                    
                    # Reset counter when we find a new message
                    consecutive_old = 0
                    
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
                    
                    # Save to database (will go to category-specific table too) with safe locking
                    db_success = await self._safe_db_write(self.db.insert_message, message_data)
                    if not db_success:
                        logger.warning(f"⚠️  Database write failed for message {message_id} after retries, saving to CSV only")
                    
                    # Always save to CSV (even if DB write failed)
                    try:
                        self.csv_handler.write_message(message_data)
                    except Exception as csv_error:
                        logger.error(f"❌ CSV write error for message {message_id}: {csv_error}")
                    
                    # Update tracking and count even if DB write failed (CSV backup exists)
                    self.processed_messages.add(message_id)
                    messages.append(message_data)
                    new_messages_count += 1
                    
                    logger.info(f"Fetched job message: {job_type} from {group_name}")
                
                # Update account usage with safe locking (non-critical, continue even if it fails)
                if new_messages_count > 0:
                    try:
                        usage_success = await self._safe_db_write(
                            self.db.update_account_usage,
                            account['name'],
                            messages_fetched=new_messages_count
                        )
                        if not usage_success:
                            logger.debug(f"Account usage update failed for {account['name']} (non-critical)")
                    except Exception as usage_error:
                        logger.debug(f"Account usage update error (non-critical): {usage_error}")
                
                # Log with more detail
                if new_messages_count > 0:
                    logger.info(f"✅ Fetched {new_messages_count} new job messages from {group_name} (checked {messages_checked} total)")
                else:
                    logger.debug(f"⏭️  No new messages in {group_name} (checked {messages_checked})")
                
                return messages
            
            except asyncio.TimeoutError:
                logger.error(f"⏱️  Timeout fetching messages from {group_link} (attempt {retry + 1}/{max_retries})")
                if retry < max_retries - 1:
                    await asyncio.sleep(10)
                    continue
                return []
            
            except FloodWaitError as e:
                logger.warning(f"⚠️  FloodWait error: need to wait {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
                return []
            
            except (ConnectionError, OSError, ServerError, RpcCallFailError, AttributeError) as e:
                error_str = str(e).lower()
                is_disconnected = 'disconnected' in error_str or 'cannot send' in error_str
                
                logger.warning(f"🔌 Network error fetching from {group_link}: {e} (attempt {retry + 1}/{max_retries})")
                
                if is_disconnected and client_info and client_info.get('client'):
                    try:
                        # Try to reconnect the client
                        logger.info("🔄 Attempting to reconnect client...")
                        client = client_info['client']
                        if not client.is_connected():
                            await client.connect()
                            logger.info("✅ Client reconnected successfully")
                        else:
                            # Force reconnect
                            await client.disconnect()
                            await asyncio.sleep(2)
                            await client.connect()
                            logger.info("✅ Client reconnected successfully")
                    except Exception as reconnect_error:
                        logger.warning(f"⚠️  Reconnection failed: {reconnect_error}")
                
                if retry < max_retries - 1:
                    # Exponential backoff: 15s, 30s, 45s
                    wait_time = min(15 * (retry + 1), 45)
                    logger.info(f"Network issue detected, retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                return []
            
            except sqlite3.OperationalError as e:
                if 'database is locked' in str(e):
                    logger.warning(f"💾 Database locked, waiting... (attempt {retry + 1}/{max_retries})")
                    # Exponential backoff: 5s, 10s, 20s, 30s
                    wait_time = min(5 * (2 ** retry), 30)
                    await asyncio.sleep(wait_time)
                    if retry < max_retries - 1:
                        continue
                logger.error(f"Database error: {e}")
                return []
            
            except Exception as e:
                logger.error(f"❌ Error fetching messages from {group_link}: {type(e).__name__}: {e}")
                if retry < max_retries - 1 and not self.is_shutting_down:
                    await asyncio.sleep(10)
                    continue
                return []
        
        return []
    
    async def process_groups(self, groups_data):
        """Process list of groups with optimized speed"""
        logger.info(f"Starting to process {len(groups_data)} groups...")
        
        start_time = datetime.now()
        groups_with_messages = 0
        total_messages = 0
        
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
                        logger.info(f"⏭️  Skipped joining {group.get('name', 'Unknown')} [{i+1}/{len(groups_data)}]")
                        continue
                
                # Fetch messages
                messages = await self.fetch_messages(group_link, client_info)
                
                if messages:
                    groups_with_messages += 1
                    total_messages += len(messages)
                
                # Progress with statistics
                elapsed = (datetime.now() - start_time).total_seconds()
                avg_time_per_group = elapsed / (i + 1)
                remaining_groups = len(groups_data) - (i + 1)
                eta_seconds = avg_time_per_group * remaining_groups
                eta_minutes = int(eta_seconds / 60)
                
                logger.info(f"📊 Progress: {i+1}/{len(groups_data)} | "
                          f"Messages: {total_messages} from {groups_with_messages} groups | "
                          f"ETA: {eta_minutes}min")
                
                # Reduced delay between groups (only if request_delay is set)
                request_delay = RATE_LIMITS.get('request_delay', (2, 5))
                await self._safe_delay(request_delay)
                
            except Exception as e:
                logger.error(f"Error processing group {group.get('name', 'Unknown')}: {e}")
                continue
        
        # Final summary
        total_time = (datetime.now() - start_time).total_seconds() / 60
        logger.info(f"✅ Completed! Processed {len(groups_data)} groups in {total_time:.1f} minutes. "
                   f"Found {total_messages} messages from {groups_with_messages} groups.")
    
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
        """Close all client connections gracefully"""
        logger.info("Closing all client connections...")
        
        for client_info in self.clients:
            try:
                client = client_info['client']
                account_name = client_info['account']['name']
                
                if client.is_connected():
                    logger.info(f"Disconnecting {account_name}...")
                    
                    # Cancel any pending tasks gracefully
                    try:
                        # Give client time to finish pending operations
                        await asyncio.wait_for(client.disconnect(), timeout=15)
                        logger.info(f"✅ {account_name} disconnected cleanly")
                    except asyncio.TimeoutError:
                        logger.warning(f"⏱️  Timeout disconnecting {account_name}, forcing...")
                        # Force disconnect if timeout
                        try:
                            await asyncio.wait_for(client.disconnect(), timeout=5)
                        except:
                            pass
                else:
                    logger.debug(f"{account_name} already disconnected")
                    
            except Exception as e:
                logger.error(f"Error disconnecting {client_info['account']['name']}: {e}")
                # Continue with other clients
                continue
        
        # Cancel any remaining background tasks
        for task in self._running_tasks:
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=5)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
        
        logger.info("✅ All clients disconnected successfully")

