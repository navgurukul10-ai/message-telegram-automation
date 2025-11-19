# 🔧 Automatic Maintenance System

## Overview

आपकी `daily_run.py` script अब **automatically** ये काम करती है:

1. ✅ **Empty job types fix करना** - जो messages में job_type missing है उन्हें classify करना
2. ✅ **CSV files को database के साथ sync करना** - हर run से पहले और बाद में

## 🚀 Changes Made

### 1. New Module: `src/utils/maintenance.py`

एक नया utility module बनाया गया है जिसमें ये functions हैं:

- `fix_empty_job_types()` - Empty job types को automatically classify और fix करता है
- `sync_csv_with_database()` - Database से CSV files export करता है
- `perform_maintenance()` - Dono functions को automatically run करता है

### 2. Enhanced `scripts/daily_run.py`

अब daily_run.py में automatic maintenance integrated है:

**पहले:**
```python
async def daily_main():
    # Initialize clients
    # Run continuous
```

**अब:**
```python
async def daily_main():
    # Step 1: Perform maintenance (fix job types + sync CSV)
    perform_maintenance()
    
    # Step 2: Initialize clients
    # Step 3: Run continuous
    
    # Step 4: Final maintenance after fetching
    perform_maintenance()
```

## 📊 What Happens Automatically

### When you run `python3 daily_run.py`:

1. **Start-up Maintenance:**
   - Empty job types fix होते हैं
   - CSV files database के साथ sync होती हैं
   - Backups automatically बनती हैं

2. **Normal Operation:**
   - Telegram से messages fetch होते हैं
   - Database में save होते हैं
   - CSV में real-time append होते हैं

3. **Final Maintenance:**
   - फिर से CSV sync होता है
   - Latest data ensure होता है

## 🎯 Benefits

### अब आपको manually ये scripts नहीं चलानी पड़ेंगी:

❌ ~~`python3 fix_job_types.py`~~
❌ ~~`python3 scripts/sync_csv_with_db.py`~~

✅ सिर्फ एक command: `python3 daily_run.py`

## 📈 Results

### Database और CSV में consistency:

```bash
# Database में:
- Total messages: 292
- Tech jobs: 240
- Non-tech jobs: 42
- Freelance jobs: 10 (1 freelance + 2 freelance_non_tech + 7 freelance_tech)

# CSV में (after sync):
- all_messages.csv: 292 rows ✅
- tech_jobs.csv: 247 rows ✅
- non_tech_jobs.csv: 42 rows ✅
- freelance_jobs.csv: 10 rows ✅
- joined_groups.csv: 10 rows ✅
```

## 🔄 Backup System

हर sync से पहले automatic backups बनती हैं:

```
freelance_jobs.csv                    <- Latest (synced with DB)
freelance_jobs.csv.backup.1759898448  <- Previous version
```

## 🧪 Manual Testing

अगर आप manually maintenance test करना चाहें:

```bash
# Test maintenance only
python3 -c "from src.utils.maintenance import perform_maintenance; perform_maintenance()"

# Test job type fixing only
python3 -c "from src.utils.maintenance import fix_empty_job_types; fix_empty_job_types()"

# Test CSV sync only
python3 -c "from src.utils.maintenance import sync_csv_with_database; sync_csv_with_database()"
```

## 📝 Logs

Maintenance activities logged होती हैं:

```
logs/maintenance_YYYYMMDD.log
logs/daily_run_YYYYMMDD.log
```

## ⚙️ Configuration

Maintenance automatic है, लेकिन अगर customize करना हो:

Edit: `src/utils/maintenance.py`

```python
# Skip job type fixing
def perform_maintenance(skip_job_fix=False):
    if not skip_job_fix:
        fix_empty_job_types()
    sync_csv_with_database()
```

## 🎉 Summary

अब जब भी आप `python3 daily_run.py` चलाएंगे:

1. ✅ सभी job types automatically fix हो जाएंगे
2. ✅ CSV files database के साथ sync हो जाएंगी
3. ✅ Backups automatically बनेंगी
4. ✅ कोई manual intervention नहीं चाहिए

**Just run once daily, everything else is automatic! 🚀**

