# 🛡️ TELEGRAM ACCOUNT SAFETY GUIDE

## ⚠️ CRITICAL: READ THIS BEFORE RUNNING

This guide contains **ESSENTIAL** safety practices to avoid Telegram account bans.

---

## 🚨 UPDATED SAFE RATE LIMITS

### Current Configuration (SAFE!)

```python
RATE_LIMITS = {
    'join_group_delay': (1800, 3600),  # 30-60 minutes (HUMAN-LIKE!)
    'max_groups_per_day': 2,           # Max 2 groups per account per day
    'max_groups_per_hour': 1,          # Max 1 group per hour
    'daily_message_limit': 75,         # Max 75 messages per group
    'working_hours': (10, 20),         # Only 10 AM - 8 PM
}
```

### Per Account Daily Limits

✅ **Join: 2 groups maximum**
✅ **Read: 75 messages per group**
✅ **Delay between joins: 30-60 minutes**
✅ **Active time: 2-3 hours spread across day**
✅ **Working hours: 10 AM - 8 PM only**

### Global (4 Accounts)

✅ **Total joins: 8 groups/day maximum**
✅ **Total messages: 600 messages/day**
✅ **Peak activity: Human hours only**

---

## ✅ WHAT WE'VE IMPLEMENTED

### 1. Conservative Rate Limiting
- ✅ 30-60 minute delays between group joins
- ✅ Only 2 groups per account per day
- ✅ 75 messages per group (not unlimited)
- ✅ Working hours restriction (10 AM - 8 PM)
- ✅ Random delays (5-15 seconds)

### 2. Enhanced Data Collection
- ✅ Separate tables: tech_jobs, non_tech_jobs, freelance_jobs
- ✅ Company name extraction
- ✅ Company website detection
- ✅ LinkedIn profile detection
- ✅ Skills extraction
- ✅ Salary range parsing
- ✅ Experience requirements
- ✅ Work mode (Remote/Hybrid/Onsite)
- ✅ Contact information
- ✅ Job verification scoring

### 3. Year Filtering
- ✅ Only fetches messages from 2025
- ✅ Filters old messages automatically

### 4. Smart Job Verification
- ✅ Validates job posts before storing
- ✅ Calculates verification score (0-100%)
- ✅ Extracts detailed company information
- ✅ Minimum description length check

---

## 🚫 WHAT TRIGGERS BANS

### Immediate Ban Risks
❌ **Joining 10+ groups quickly**
❌ **No delays between actions**
❌ **Consistent patterns (no randomness)**
❌ **24/7 automation**
❌ **Reading thousands of messages**

### Medium Ban Risks
⚠️ **Joining 5-10 groups/day**
⚠️ **Short delays (< 5 minutes)**
⚠️ **High message fetch rates**
⚠️ **Using new accounts**

### Safe Practices
✅ **2-3 groups/day maximum**
✅ **30-60 minute delays**
✅ **Random variations**
✅ **Working hours only**
✅ **Old accounts (6+ months)**

---

## 📊 DATABASE STRUCTURE

### Separate Tables Created

1. **tech_jobs**
   - All technical job postings
   - Enhanced with company info
   - Verification scores

2. **non_tech_jobs**
   - Non-technical positions
   - Marketing, Sales, HR, etc.
   - Same enhanced fields

3. **freelance_jobs**
   - Freelance/Contract work
   - Remote opportunities
   - Gig economy jobs

4. **messages**
   - Backup table with all messages
   - Quick reference

### Enhanced Fields

Each job table includes:
```sql
- company_name
- company_website
- company_linkedin
- skills_required
- salary_range
- job_location
- work_mode (Remote/Hybrid/Onsite)
- experience_required
- job_type (Full-time/Part-time)
- application_deadline
- contact_info
- is_verified (Boolean)
- verification_score (0-100)
```

---

## 🔍 JOB VERIFICATION SYSTEM

### Verification Criteria

Jobs are scored based on:
1. **Company Name** (30 points)
2. **Contact Info** (20 points)
3. **Company Website** (15 points)
4. **LinkedIn Profile** (10 points)
5. **Skills Listed** (10 points)
6. **Salary Range** (5 points)
7. **Experience** (5 points)
8. **Work Mode** (5 points)

**Total: 100 points**

### Verification Status

- **is_verified = True**: Score >= 50%
- **is_verified = False**: Score < 50%

---

## 📈 EXPECTED PERFORMANCE (30 DAYS)

### With SAFE Limits

```
Per Account:
- Groups joined: 60 (2/day × 30 days)
- Messages fetched: ~4,500 (75 × 60)

All 4 Accounts:
- Total groups: 240
- Total messages: ~18,000
- Job postings: ~3,000-5,000 (estimated)

Ban Risk: ⚠️ VERY LOW (if limits respected)
```

### Previous RISKY Limits (DON'T USE!)

```
❌ 15 groups/day = 450 groups (TOO MUCH!)
❌ 500 messages/day = 15,000/day (DANGEROUS!)
❌ 60-120 sec delays (TOO FAST!)
```

---

## 🛠️ HOW TO VERIFY SYSTEM IS WORKING

### 1. Check Database Tables

```bash
sqlite3 data/database/telegram_jobs.db

SELECT COUNT(*) FROM tech_jobs;
SELECT COUNT(*) FROM non_tech_jobs;
SELECT COUNT(*) FROM freelance_jobs;
```

### 2. Verify Enhanced Fields

```sql
SELECT company_name, company_website, verification_score, is_verified 
FROM tech_jobs 
LIMIT 10;
```

### 3. Check Year Filter

```sql
SELECT date FROM messages ORDER BY date DESC LIMIT 10;
-- All should be from 2025
```

### 4. Monitor Rate Limits

```bash
tail -f logs/telegram_client_$(date +%Y%m%d).log
```

Look for:
- ✅ "Waiting 1800-3600 seconds" (30-60 min delays)
- ✅ "Outside working hours" (time restrictions)
- ✅ "Daily limits reached" (account protection)

---

## ⚡ QUICK START (SAFE MODE)

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Authorize (One-time)
```bash
python3 main.py --auth
```

### 3. Run (Safe Limits Active)
```bash
python3 main.py
```

### 4. Monitor
```bash
python3 check_status.py
```

---

## 📋 DAILY CHECKLIST

- [ ] Check logs for errors
- [ ] Verify no FloodWait warnings
- [ ] Confirm working hours respected
- [ ] Check group join count (should be ~8/day)
- [ ] Verify messages from 2025 only
- [ ] Check verification scores
- [ ] Backup database

---

## 🚀 WHAT'S IMPROVED

### Old System → New System

| Feature | Old | New | Status |
|---------|-----|-----|--------|
| Groups/day | 15 | 2 | ✅ SAFE |
| Join delay | 60-120s | 1800-3600s | ✅ SAFE |
| Messages/group | 100 | 75 | ✅ SAFE |
| Working hours | 24/7 | 10AM-8PM | ✅ SAFE |
| Database tables | 1 | 3 + backup | ✅ IMPROVED |
| Year filter | No | Yes (2025) | ✅ ADDED |
| Job verification | No | Yes | ✅ ADDED |
| Company info | No | Yes | ✅ ADDED |

---

## ⚠️ IMPORTANT WARNINGS

### DO NOT:
❌ Modify rate limits to be more aggressive
❌ Remove working hours restriction
❌ Increase groups per day
❌ Run multiple instances simultaneously
❌ Use on personal Telegram accounts

### DO:
✅ Let the system run with current limits
✅ Monitor logs daily
✅ Respect working hours
✅ Use dedicated accounts
✅ Keep accounts active manually

---

## 📞 IF YOU GET BANNED

### Signs of Ban:
- "FloodWaitError" in logs
- Cannot join groups
- "Too many requests" errors
- Account restrictions

### Immediate Actions:
1. **STOP the script immediately**
2. **Wait 24-48 hours**
3. **Review rate limits**
4. **Check if you modified anything**
5. **Restart with even safer limits**

### Recovery:
- Reduce groups to 1/day
- Increase delays to 1 hour
- Work only 2-3 hours/day
- Use different account rotation

---

## ✅ SUCCESS INDICATORS

Your system is working correctly if:

✅ **No "FloodWait" errors**
✅ **Groups joined: ~8/day total**
✅ **Messages from 2025 only**
✅ **Separate tables populated**
✅ **Verification scores calculated**
✅ **Company names extracted**
✅ **Working hours respected**
✅ **30-60 min delays between joins**

---

## 📊 MONITORING COMMANDS

```bash
# Check overall status
python3 check_status.py

# View tech jobs
sqlite3 data/database/telegram_jobs.db "SELECT * FROM tech_jobs LIMIT 10;"

# Check verification scores
sqlite3 data/database/telegram_jobs.db \
  "SELECT AVG(verification_score) FROM tech_jobs;"

# Count by category
sqlite3 data/database/telegram_jobs.db \
  "SELECT 'Tech', COUNT(*) FROM tech_jobs
   UNION
   SELECT 'Non-Tech', COUNT(*) FROM non_tech_jobs
   UNION
   SELECT 'Freelance', COUNT(*) FROM freelance_jobs;"
```

---

## 🎯 FINAL RECOMMENDATIONS

1. **Be Patient**: Slow and steady wins the race
2. **Monitor Daily**: Check logs and stats
3. **Trust the Limits**: They're set for safety
4. **Don't Be Greedy**: 2 groups/day is enough
5. **Quality Over Quantity**: Verified jobs are better
6. **Stay Safe**: No bans = Long-term success

---

**Remember**: Better to collect 5,000 quality jobs safely than 50,000 jobs and get banned! 🛡️

