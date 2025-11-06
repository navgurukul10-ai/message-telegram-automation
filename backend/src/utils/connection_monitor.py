"""
Connection monitoring and recovery utility
Helps maintain stable connections and recover from network issues
"""
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('connection_monitor')

class ConnectionMonitor:
    """Monitor and manage Telegram client connections"""
    
    def __init__(self, check_interval=300):
        """
        Initialize connection monitor
        
        Args:
            check_interval: Seconds between connection health checks (default 5 minutes)
        """
        self.check_interval = check_interval
        self.connection_stats = {}
        self.is_monitoring = False
        self._monitor_task = None
    
    def register_client(self, client_name, client):
        """Register a client for monitoring"""
        self.connection_stats[client_name] = {
            'client': client,
            'last_check': None,
            'last_success': None,
            'failures': 0,
            'reconnects': 0,
            'status': 'unknown'
        }
        logger.info(f"Registered {client_name} for connection monitoring")
    
    async def check_connection(self, client_name):
        """Check if a specific client connection is healthy"""
        if client_name not in self.connection_stats:
            return False
        
        stats = self.connection_stats[client_name]
        client = stats['client']
        stats['last_check'] = datetime.now()
        
        try:
            # Try a simple API call to verify connection
            if client.is_connected():
                # Ping test with timeout
                await asyncio.wait_for(client.get_me(), timeout=10)
                stats['last_success'] = datetime.now()
                stats['failures'] = 0
                stats['status'] = 'healthy'
                logger.debug(f"✅ {client_name} connection healthy")
                return True
            else:
                stats['status'] = 'disconnected'
                logger.warning(f"⚠️  {client_name} is disconnected")
                return False
                
        except asyncio.TimeoutError:
            stats['failures'] += 1
            stats['status'] = 'timeout'
            logger.warning(f"⏱️  {client_name} connection timeout (failures: {stats['failures']})")
            return False
            
        except Exception as e:
            stats['failures'] += 1
            stats['status'] = 'error'
            logger.error(f"❌ {client_name} connection check failed: {e} (failures: {stats['failures']})")
            return False
    
    async def attempt_reconnect(self, client_name):
        """Attempt to reconnect a failed client"""
        if client_name not in self.connection_stats:
            return False
        
        stats = self.connection_stats[client_name]
        client = stats['client']
        
        try:
            logger.info(f"🔄 Attempting to reconnect {client_name}...")
            
            # Disconnect first if partially connected
            if client.is_connected():
                await asyncio.wait_for(client.disconnect(), timeout=10)
            
            # Wait a bit before reconnecting
            await asyncio.sleep(5)
            
            # Reconnect
            await asyncio.wait_for(client.connect(), timeout=60)
            
            # Verify reconnection
            if await self.check_connection(client_name):
                stats['reconnects'] += 1
                stats['failures'] = 0
                logger.info(f"✅ Successfully reconnected {client_name} (total reconnects: {stats['reconnects']})")
                return True
            else:
                logger.error(f"❌ Reconnection verification failed for {client_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to reconnect {client_name}: {e}")
            return False
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🔍 Connection monitoring started")
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                for client_name in list(self.connection_stats.keys()):
                    # Check connection health
                    is_healthy = await self.check_connection(client_name)
                    
                    # If unhealthy and has failures, attempt reconnect
                    stats = self.connection_stats[client_name]
                    if not is_healthy and stats['failures'] >= 2:
                        logger.warning(f"⚠️  {client_name} has {stats['failures']} failures, attempting reconnect...")
                        await self.attempt_reconnect(client_name)
                    
                    # Small delay between checks
                    await asyncio.sleep(2)
                
                # Wait before next monitoring cycle
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logger.info("Connection monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait a minute on error
        
        logger.info("Connection monitoring stopped")
    
    def start_monitoring(self):
        """Start background monitoring"""
        if not self.is_monitoring:
            self._monitor_task = asyncio.create_task(self.monitor_loop())
            logger.info("Started connection monitoring task")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await asyncio.wait_for(self._monitor_task, timeout=10)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        logger.info("Stopped connection monitoring")
    
    def get_stats(self):
        """Get current connection statistics"""
        return {
            name: {
                'status': stats['status'],
                'failures': stats['failures'],
                'reconnects': stats['reconnects'],
                'last_check': stats['last_check'].isoformat() if stats['last_check'] else None,
                'last_success': stats['last_success'].isoformat() if stats['last_success'] else None
            }
            for name, stats in self.connection_stats.items()
        }
    
    def print_status(self):
        """Print current connection status"""
        print("\n" + "="*60)
        print("CONNECTION STATUS")
        print("="*60)
        
        for name, stats in self.connection_stats.items():
            status_emoji = {
                'healthy': '✅',
                'disconnected': '❌',
                'timeout': '⏱️',
                'error': '⚠️',
                'unknown': '❓'
            }.get(stats['status'], '❓')
            
            print(f"\n{status_emoji} {name}")
            print(f"  Status: {stats['status']}")
            print(f"  Failures: {stats['failures']}")
            print(f"  Reconnects: {stats['reconnects']}")
            if stats['last_success']:
                print(f"  Last Success: {stats['last_success'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*60 + "\n")

