# Quick Start Guide 🚀

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Or run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

### 2. Authorize Accounts (One-time)
```bash
python main.py --auth
```

Enter the verification code sent to each phone number when prompted.

### 3. Start Fetching
```bash
python main.py
```

That's it! The system will now:
- Join groups from `data.json`
- Fetch job messages from 2024
- Classify jobs (tech/non-tech/freelance)
- Save to CSV, JSON, and database
- Run continuously for 30 days

## Check Status

```bash
python check_status.py
```

## Monitor Real-time

```bash
# Watch main log
tail -f logs/main_$(date +%Y%m%d).log

# Watch telegram client log
tail -f logs/telegram_client_$(date +%Y%m%d).log
```

## View Results

### CSV Files (Easy to open in Excel)
```bash
# All messages
cat data/csv/all_messages.csv

# Tech jobs only
cat data/csv/tech_jobs.csv

# Non-tech jobs
cat data/csv/non_tech_jobs.csv

# Freelance jobs
cat data/csv/freelance_jobs.csv

# Joined groups
cat data/csv/joined_groups.csv
```

### Database Queries
```bash
sqlite3 data/database/telegram_jobs.db

# Inside SQLite:
SELECT COUNT(*) FROM messages;
SELECT job_type, COUNT(*) FROM messages GROUP BY job_type;
SELECT * FROM groups LIMIT 10;
```

## Important Safety Limits

✅ **Max 15 groups per day** per account (to avoid bans)
✅ **1-2 minute delay** between joining groups
✅ **5-10 second delay** between message fetches
✅ **Account rotation** to distribute load

**DO NOT modify these limits!** They're set to keep accounts safe.

## Troubleshooting

### Problem: "No clients initialized"
**Solution:** Run `python main.py --auth` first

### Problem: FloodWait errors
**Solution:** System handles automatically. Just wait.

### Problem: No messages fetched
**Check:**
- Groups in data.json are valid
- Year filter is correct (2024)
- Messages contain job keywords

## Stop the System

Press `Ctrl + C` to stop gracefully.

## Next Steps

- Monitor logs for any errors
- Check status regularly with `check_status.py`
- Analyze CSV files for job data
- Adjust keywords in `config.py` if needed

---

Need more details? Check `README.md`

