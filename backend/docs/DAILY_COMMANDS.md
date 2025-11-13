# 📋 Daily Commands - रोज़ ये use करो

## 🌅 **Morning Routine (सुबह 10 AM):**

### **Step 1: Data Collect करो**

```bash
# Option A: Script से
./run_today.sh

# Option B: Direct command
python3 daily_run.py
```

**Time:** 2-3 घंटे laptop ON रखो

---

## 🌐 **Afternoon: Results देखो (दोपहर 1-2 PM):**

### **Web Dashboard (Browser में - Beautiful!):**

```bash
# Start dashboard
./start_dashboard.sh

# या direct:
python3 web_dashboard.py
```

**फिर browser में खोलो:**
```
http://localhost:7000
```

**या**
```
http://127.0.0.1:7000
```

### **दिखेगा:**
- ✅ Date-wise groups joined
- ✅ Date-wise jobs count (Tech/Non-Tech/Freelance)
- ✅ Best jobs with company info
- ✅ Full messages
- ✅ Beautiful colorful UI
- ✅ Auto-refresh

---

### **Terminal Dashboard (Fast!):**

```bash
python3 view_dashboard.py
```

**Terminal में ही सब दिखेगा:**
- Date-wise breakdown
- Groups info
- Job counts
- Best jobs
- Interactive menu

---

### **Quick Status:**

```bash
python3 check_status.py
```

**Quick summary दिखेगा:**
- Total jobs
- Groups joined
- Today's stats

---

## 📊 **What You'll See in UI:**

### **Port 7000 पर Web Dashboard:**

```
Browser: http://localhost:7000

╔═══════════════════════════════════════════════════╗
║      📊 Telegram Job Fetcher Dashboard           ║
╚═══════════════════════════════════════════════════╝

[Colorful Cards]
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ 🔧 Tech │  │💼 Non   │  │🏖️ Free │  │🔗Groups │
│  1,234  │  │  567    │  │  890    │  │  240    │
└─────────┘  └─────────┘  └─────────┘  └─────────┘

📅 Groups Joined (Date-wise)
─────────────────────────────────────────────────
Date          Groups    Names
─────────────────────────────────────────────────
2025-01-08      8      TechJobs, PythonDev, ...
2025-01-07      8      DevOps, AIJobs, ...

📊 Jobs Collected (Date-wise)  
─────────────────────────────────────────────────
Date        Tech  Non-Tech  Freelance  Total
─────────────────────────────────────────────────
2025-01-08   45      23        32       100
2025-01-07   52      18        27        97

⭐ Best Verified Jobs
─────────────────────────────────────────────────
[Tabs: Best | Tech | Non-Tech | Freelance]

Google India ⭐ 95.5%
Skills: Python, Django, AWS
Salary: ₹20-30 LPA
Mode: Remote
Date: 2025-01-08
[Full message...]
```

---

## 🔄 **Complete Daily Flow:**

```
10:00 AM
  → python3 daily_run.py (Start)
  
10:05 AM
  → Joining groups...
  → Fetching messages...
  
12:30 PM
  → Done! (Script auto-stops)
  
1:00 PM
  → python3 web_dashboard.py
  → Browser: http://localhost:7000
  → देखो सब data!
  
2:00 PM
  → Laptop बंद कर सकते हो ✅
  
Next Day 10:00 AM
  → फिर से python3 daily_run.py
  → NEW data collect होगा
  → Duplicates skip होंगे
```

---

## 📝 **Quick Reference:**

| Task | Command |
|------|---------|
| Data Collect | `python3 daily_run.py` |
| Web UI | `python3 web_dashboard.py` |
| Terminal UI | `python3 view_dashboard.py` |
| Quick Status | `python3 check_status.py` |
| Check Auth | `python3 check_auth.py` |
| Full Report | `python3 generate_report.py` |

---

## 🌐 **Web Dashboard URLs:**

```
Main Dashboard:     http://localhost:7000/

API Endpoints (JSON):
  Stats:            http://localhost:7000/api/stats
  Daily Stats:      http://localhost:7000/api/daily_stats
  Groups by Date:   http://localhost:7000/api/groups_by_date
  Best Jobs:        http://localhost:7000/api/best_jobs
  Tech Messages:    http://localhost:7000/api/messages/tech
  Non-Tech:         http://localhost:7000/api/messages/non_tech
  Freelance:        http://localhost:7000/api/messages/freelance
```

---

## 💾 **Data Locations:**

### Database:
```
data/database/telegram_jobs.db

Tables:
  - tech_jobs      (Tech job posts)
  - non_tech_jobs  (Non-tech posts)
  - freelance_jobs (Freelance work)
  - groups         (Joined groups with dates)
  - messages       (All messages backup)
```

### CSV Files:
```
data/csv/
  ├─ tech_jobs.csv
  ├─ non_tech_jobs.csv
  ├─ freelance_jobs.csv
  └─ joined_groups.csv
```

### Logs:
```
logs/
  ├─ main_20250106.log
  ├─ telegram_client_20250106.log
  └─ database_20250106.log
```

---

## ✅ **Final Checklist:**

- [x] All 4 accounts authorized
- [x] Database tables created
- [x] Duplicate prevention working
- [x] Web UI ready (Port 7000)
- [x] Terminal UI ready
- [x] CSV export working
- [x] Logs configured
- [x] Safe rate limits set
- [x] Year filter (2025) active
- [x] Company info extraction ready

---

## 🚀 **Ready to Start!**

```bash
# Daily data collection
python3 daily_run.py

# View results (Port 7000)
python3 web_dashboard.py

# Browser में खोलो
http://localhost:7000
```

**सब set है! Start करो! 🎉**

