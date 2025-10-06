# Telegram Job Fetcher 🚀

An automated system to fetch and classify job postings from Telegram groups with built-in safety features to avoid account bans.

## 📋 Features

- **Multi-Account Support**: Rotate between 4 Telegram accounts to distribute load
- **Smart Rate Limiting**: Built-in delays and limits to avoid Telegram bans
- **Job Classification**: Automatically categorizes jobs into:
  - Tech Jobs
  - Non-Tech Jobs
  - Freelance Jobs
- **Duplicate Detection**: Tracks processed messages to avoid duplicates
- **Comprehensive Logging**: Detailed logs for every action
- **Multiple Export Formats**: CSV, JSON, and SQLite database
- **Continuous Operation**: Runs for 30 days, checking hourly for new messages
- **Year Filtering**: Only fetches messages from 2024

## 🏗️ Project Structure

```
simul_automation/
├── config.py                 # Configuration settings
├── main.py                   # Main entry point
├── telegram_client.py        # Telegram client with safety features
├── data.json                 # List of Telegram groups
├── requirements.txt          # Python dependencies
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Logging utility
│   ├── database.py          # Database handler
│   ├── classifier.py        # Message classifier
│   └── csv_handler.py       # CSV export handler
├── data/
│   ├── csv/                 # CSV exports
│   │   ├── all_messages.csv
│   │   ├── tech_jobs.csv
│   │   ├── non_tech_jobs.csv
│   │   ├── freelance_jobs.csv
│   │   └── joined_groups.csv
│   ├── json/                # JSON tracking files
│   └── database/            # SQLite database
├── logs/                    # Application logs
└── sessions/                # Telegram session files

```

## 🔧 Installation

### 1. Clone or Navigate to Project Directory
```bash
cd /home/navgurukul/simul_automation
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Accounts
Your accounts are already configured in `config.py`. Make sure all API credentials are correct.

## 🚀 Usage

### First Time Setup (Authorization)

Before running the main script, you need to authorize each Telegram account:

```bash
python main.py --auth
```

Follow the prompts to enter the verification code sent to each phone number.

### Start Fetching

Once authorized, start the continuous fetching:

```bash
python main.py
```

This will:
- Join groups from `data.json`
- Fetch messages from 2024
- Classify and store job postings
- Run continuously for 30 days
- Check for new messages every hour

## ⚙️ Configuration

### Rate Limits (config.py)

To avoid bans, these limits are enforced:

```python
RATE_LIMITS = {
    'join_group_delay': (60, 120),      # 1-2 min between joins
    'message_fetch_delay': (5, 10),     # 5-10 sec between fetches
    'max_groups_per_day': 15,           # Max 15 groups per day
    'max_groups_per_hour': 3,           # Max 3 groups per hour
    'daily_message_limit': 500,         # Max 500 messages per day
}
```

### Adjusting Keywords

Edit `JOB_KEYWORDS` in `config.py` to customize job classification:

```python
JOB_KEYWORDS = {
    'tech': ['python', 'java', 'developer', ...],
    'non_tech': ['marketing', 'sales', 'hr', ...],
    'freelance': ['freelance', 'contract', 'remote', ...]
}
```

## 📊 Output Files

### CSV Files (data/csv/)
- `all_messages.csv` - All fetched job messages
- `tech_jobs.csv` - Technology job postings
- `non_tech_jobs.csv` - Non-technical job postings
- `freelance_jobs.csv` - Freelance opportunities
- `joined_groups.csv` - List of joined groups with metadata

### Database (data/database/)
- `telegram_jobs.db` - SQLite database with all data
  - Tables: messages, groups, daily_stats, account_usage

### Logs (logs/)
- Daily log files with detailed execution information
- Format: `{component}_{YYYYMMDD}.log`

## 🛡️ Safety Features

### Account Protection

1. **Rate Limiting**: Enforces delays between actions
2. **Account Rotation**: Distributes load across 4 accounts
3. **Daily Limits**: Prevents excessive usage per account
4. **Flood Wait Handling**: Automatically waits when rate limited
5. **Error Recovery**: Continues operation despite errors

### Best Practices Implemented

✅ Random delays between actions (human-like behavior)
✅ Maximum groups per day limit (15 per account)
✅ Account rotation to distribute load
✅ Graceful handling of flood wait errors
✅ Session persistence (no repeated logins)
✅ Respect for Telegram's rate limits

## 📈 Monitoring

### Check Logs
```bash
# View today's log
tail -f logs/main_$(date +%Y%m%d).log

# View telegram client log
tail -f logs/telegram_client_$(date +%Y%m%d).log
```

### Database Queries
```bash
sqlite3 data/database/telegram_jobs.db

# Check statistics
SELECT COUNT(*) FROM messages;
SELECT job_type, COUNT(*) FROM messages GROUP BY job_type;
SELECT * FROM daily_stats ORDER BY date DESC LIMIT 7;
```

### CSV Files
Open CSV files in Excel, Google Sheets, or any CSV viewer to analyze data.

## 🔄 Continuous Operation

The system runs continuously for 30 days:
1. Processes all groups from `data.json`
2. Fetches new messages every hour
3. Automatically handles errors and retries
4. Logs all activities
5. Exports data in real-time

## ⚠️ Important Notes

### Avoiding Bans

1. **DO NOT** modify rate limits to be more aggressive
2. **DO NOT** join more than 15 groups per day per account
3. **DO** let the system handle delays automatically
4. **DO** monitor logs for flood wait warnings

### Account Safety

- Use dedicated accounts (not your personal account)
- Have Telegram 2FA disabled on automation accounts
- Keep sessions secure (don't share session files)
- Monitor for ban warnings in logs

### Legal & Ethical

- Respect group rules and privacy
- Only join public groups or those you have permission to join
- Don't spam or abuse the automation
- Use responsibly and ethically

## 🐛 Troubleshooting

### Account Not Authorized
```bash
python main.py --auth
```

### FloodWait Errors
The system handles these automatically. Just wait and let it continue.

### Database Locked
```bash
# Stop the script and restart
# Ensure only one instance is running
```

### Missing Messages
Check:
- Year filter (currently set to 2024)
- Job classification keywords
- Logs for any errors

## 📞 Support

For issues or questions:
1. Check the logs directory
2. Review error messages
3. Verify configuration settings
4. Ensure API credentials are correct

## 📝 License

This project is for educational and personal use only. Respect Telegram's Terms of Service and use responsibly.

---

**Happy Job Hunting! 🎯**

