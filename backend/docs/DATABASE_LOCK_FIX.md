# Database Lock & Network Connection Fixes

## Issues Fixed

### 1. Database Lock Errors
- **Problem**: `database is locked` errors when dashboard and daily_run.py run simultaneously
- **Solution**: 
  - Increased retry attempts from 3 to 10 in `_safe_db_write`
  - Added exponential backoff (2s → 15s max)
  - Increased database handler retry delay max from 10s to 20s
  - Better connection cleanup between retries

### 2. Network Connection Errors
- **Problem**: `Cannot send requests while disconnected` and `Connection reset by peer`
- **Solution**:
  - Added automatic client reconnection on disconnect errors
  - Increased connection timeout to 120s (from 60s)
  - Increased connect wait timeout to 150s (from 90s)
  - Added exponential backoff for network retries (15s → 45s)
  - Disabled Telethon auto-reconnect to avoid AttributeError issues

## Improvements Made

### Database Lock Handling
1. **`_safe_db_write` function**:
   - Retries: 3 → 10 attempts
   - Delay between writes: 100ms → 200ms
   - Exponential backoff: 2s → 15s max
   - **Returns False instead of raising exceptions** - allows graceful handling

2. **`fetch_messages` function**:
   - Max retries: 3 → 5 attempts
   - Exponential backoff: 5s → 10s → 20s → 30s
   - **Continues processing even if DB write fails** - saves to CSV as backup
   - Better error logging

3. **`database.py` insert_message**:
   - Max retry delay: 10s → 20s

4. **Graceful Degradation**:
   - Messages saved to CSV even if database write fails
   - Processing continues instead of stopping
   - Account usage updates are non-critical (won't block processing)

### Network Connection Handling
1. **Client initialization**:
   - Timeout: 60s → 120s
   - Connect timeout: 90s → 150s
   - Network connectivity check before connection
   - Auto-reconnect disabled (manual handling)

2. **Error recovery**:
   - Automatic reconnection on disconnect
   - Exponential backoff: 15s → 30s → 45s
   - Better error detection and handling

## Usage

### Before Running daily_run.py

1. **Check for running processes**:
   ```bash
   ./check_running_processes.sh
   ```

2. **Stop dashboard if running**:
   ```bash
   pkill -f 'web_dashboard.py|dashboard/app.py'
   ```

3. **Run daily_run.py**:
   ```bash
   python3 daily_run.py
   ```

### Monitoring

Watch for these log messages:
- `💾 Database locked, waiting...` - Normal, will retry automatically
- `🔄 Attempting to reconnect client...` - Network issue, auto-reconnecting
- `✅ Client reconnected successfully` - Reconnection successful

### If Issues Persist

1. **Database still locked**:
   - Ensure dashboard is stopped: `pkill -f 'web_dashboard.py'`
   - Check database file permissions
   - Wait a few minutes and retry

2. **Network connection fails**:
   - Check internet connectivity: `ping 8.8.8.8`
   - Check Telegram server: `curl -I https://telegram.org`
   - Try again later (may be temporary Telegram server issue)
   - Check firewall/proxy settings

3. **Continuous failures**:
   - Review logs for specific error patterns
   - Check system resources (disk space, memory)
   - Consider running during off-peak hours

## Technical Details

### Database Configuration
- **WAL Mode**: Enabled for concurrent access
- **Busy Timeout**: 60 seconds
- **Synchronous**: NORMAL (balance between safety and speed)
- **Cache Size**: 64MB

### Retry Strategy
- **Database locks**: Exponential backoff (2s → 15s)
- **Network errors**: Exponential backoff (15s → 45s)
- **Max retries**: 10 for database, 3-5 for network

### Connection Settings
- **Connection timeout**: 120 seconds
- **Request timeout**: 150 seconds
- **Retry delays**: Progressive (10s → 180s max)

## Best Practices

1. **Always stop dashboard before running daily_run.py**
2. **Run during stable network conditions**
3. **Monitor logs for patterns**
4. **Use check_running_processes.sh before starting**
5. **Allow sufficient time for retries (30+ minutes for 52 groups)**

## Files Modified

1. `src/core/telegram_client.py`:
   - `_safe_db_write()`: Improved retry logic
   - `fetch_messages()`: Better error handling and reconnection
   - `_initialize_clients()`: Improved timeout settings

2. `src/storage/database.py`:
   - `insert_message()`: Increased retry delays
   - `connect()`: Better lock handling

3. New files:
   - `check_running_processes.sh`: Process checker script

