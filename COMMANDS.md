# Command Reference 🔧

## Setup Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Or use the setup script
chmod +x setup.sh
./setup.sh
```

## Authorization (One-time)

```bash
# Authorize all 4 accounts
python3 main.py --auth
```

## Running the System

```bash
# Start the fetcher (runs for 30 days)
python3 main.py

# Run in background (recommended for long runs)
nohup python3 main.py > output.log 2>&1 &

# Check if running
ps aux | grep main.py

# Stop gracefully
# Press Ctrl+C or:
kill -SIGINT <PID>
```

## Monitoring

```bash
# Check current status
python3 check_status.py

# Generate detailed report
python3 generate_report.py

# Generate report for last 30 days
python3 generate_report.py 30

# Watch logs in real-time
tail -f logs/main_$(date +%Y%m%d).log

# Watch telegram client logs
tail -f logs/telegram_client_$(date +%Y%m%d).log

# Check all logs
ls -lh logs/
```

## Data Access

```bash
# View CSV files
cat data/csv/tech_jobs.csv
cat data/csv/non_tech_jobs.csv
cat data/csv/freelance_jobs.csv

# Open in less for pagination
less data/csv/all_messages.csv

# Count messages
wc -l data/csv/all_messages.csv

# SQLite database queries
sqlite3 data/database/telegram_jobs.db

# Common queries:
sqlite3 data/database/telegram_jobs.db "SELECT COUNT(*) FROM messages;"
sqlite3 data/database/telegram_jobs.db "SELECT job_type, COUNT(*) FROM messages GROUP BY job_type;"
sqlite3 data/database/telegram_jobs.db "SELECT * FROM groups ORDER BY messages_fetched DESC LIMIT 10;"
```

## File Operations

```bash
# Backup database
cp data/database/telegram_jobs.db data/database/backup_$(date +%Y%m%d).db

# Export all CSVs
tar -czf csv_export_$(date +%Y%m%d).tar.gz data/csv/

# View project structure
tree -L 2

# Check disk usage
du -sh data/
```

## Troubleshooting

```bash
# Check for errors in logs
grep -i error logs/*.log

# Check for flood wait warnings
grep -i flood logs/*.log

# Verify Python syntax
python3 -m py_compile *.py utils/*.py

# Check dependencies
pip list | grep telethon

# Test database connection
python3 -c "import sqlite3; conn = sqlite3.connect('data/database/telegram_jobs.db'); print('OK')"
```

## Maintenance

```bash
# Clean old logs (older than 30 days)
find logs/ -name "*.log" -mtime +30 -delete

# Backup everything
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/ sessions/

# Check file sizes
ls -lh data/csv/
ls -lh data/database/

# Verify data integrity
sqlite3 data/database/telegram_jobs.db "PRAGMA integrity_check;"
```

## Quick Checks

```bash
# How many messages collected?
sqlite3 data/database/telegram_jobs.db "SELECT COUNT(*) FROM messages;"

# How many groups joined?
sqlite3 data/database/telegram_jobs.db "SELECT COUNT(*) FROM groups;"

# Latest activity
sqlite3 data/database/telegram_jobs.db "SELECT * FROM messages ORDER BY date DESC LIMIT 5;"

# Today's statistics
python3 check_status.py | grep -A 5 "Today"
```

## Process Management

```bash
# Start in background
nohup python3 main.py > output.log 2>&1 &

# Get process ID
echo $!

# Or find it
ps aux | grep "python3 main.py"

# Stop process
kill -SIGINT $(ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}')

# Check if still running
ps aux | grep main.py | grep -v grep
```

## Testing

```bash
# Test database connection
python3 -c "from utils.database import DatabaseHandler; db = DatabaseHandler(); print('Database OK')"

# Test classifier
python3 -c "from utils.classifier import MessageClassifier; c = MessageClassifier(); print(c.classify('Python developer job opening'))"

# Test CSV handler
python3 -c "from utils.csv_handler import CSVHandler; csv = CSVHandler(); print('CSV Handler OK')"

# Test logger
python3 -c "from utils.logger import get_logger; log = get_logger('test'); log.info('Test OK')"
```

---

**Pro Tip**: Create aliases for frequently used commands:

```bash
# Add to ~/.bashrc
alias tg-status='python3 /home/navgurukul/simul_automation/check_status.py'
alias tg-report='python3 /home/navgurukul/simul_automation/generate_report.py'
alias tg-logs='tail -f /home/navgurukul/simul_automation/logs/main_*.log'
```

