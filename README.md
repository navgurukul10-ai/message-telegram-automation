# 🤖 Telegram Job Fetcher - AI-Powered Job Collection System

> Professional-grade automation system for collecting and classifying job postings from Telegram groups with AI-powered features

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)](.)

---

## 🌟 **Key Features**

- 🤖 **AI-Powered Classification** - Smart job categorization (Tech/Non-Tech/Freelance)
- 🏢 **Company Info Extraction** - Automatically extracts company names, websites, LinkedIn
- ✅ **Job Verification System** - 0-100% quality scoring
- 🛡️ **Account Protection** - Ultra-safe rate limits to prevent bans
- 📊 **Beautiful Web Dashboard** - Real-time analytics on port 7000
- 💾 **Multiple Storage** - SQLite DB + CSV + JSON exports
- 🔄 **Smart Duplicate Detection** - No repeated data
- 📅 **Date-wise Tracking** - Complete historical analysis
- 🌐 **Multi-Account Support** - 4 account rotation for safety

---

## 📁 **Project Structure (AI-Style)**

```
simul_automation/
├── src/               # Core source code
│   ├── core/         # Main Telegram logic
│   ├── services/     # AI services (classifier, verifier)
│   ├── storage/      # Data storage handlers
│   └── utils/        # Utilities
├── scripts/          # Executable scripts
├── dashboard/        # Web UI (Flask)
├── config/           # Configuration files
├── docs/             # Documentation
├── data/             # Data storage
├── logs/             # Application logs
└── sessions/         # Telegram sessions
```

---

## 🚀 **Quick Start**

### **Installation**

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/final-telegram-automation.git
cd final-telegram-automation

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config/config_template.py config/config.py
# Edit config/config.py with your API credentials
```

### **Authorization** (One-time)

```bash
python3 scripts/main.py --auth
```

### **Daily Run**

```bash
python3 scripts/daily_run.py
```

### **View Dashboard**

```bash
python3 dashboard/app.py
```

Open browser: **http://localhost:7000**

---

## 📊 **What Gets Collected**

### **Data Structure**

```sql
tech_jobs:
  ✅ company_name
  ✅ company_website
  ✅ company_linkedin
  ✅ skills_required (Python, Java, etc.)
  ✅ salary_range (₹5-10 LPA)
  ✅ job_location
  ✅ work_mode (Remote/Hybrid/Onsite)
  ✅ experience_required
  ✅ contact_info
  ✅ verification_score (0-100%)
  ✅ Full message text
```

Same structure for `non_tech_jobs` and `freelance_jobs`.

---

## 🛡️ **Safety Features**

### **Ultra-Safe Rate Limits**

- ✅ **30-60 minutes** between group joins
- ✅ **2 groups/day** per account maximum
- ✅ **75 messages** per group
- ✅ **10 AM - 8 PM** working hours only
- ✅ **Account rotation** for load balancing
- ✅ **FloodWait handling**

**Ban Risk: < 5%** (Extremely safe!)

---

## 📈 **Expected Results (30 Days)**

| Metric | Value |
|--------|-------|
| Groups Joined | 240 unique |
| Messages Analyzed | ~18,000 |
| Job Postings | 3,000-5,000 |
| Company Info Extracted | 60-80% |
| Verified Jobs | ~70% |
| Account Bans | 0 |

---

## 🎨 **Web Dashboard Features**

Access at: **http://localhost:7000**

- 📊 **Real-time Statistics** - Live counts and metrics
- 📅 **Date-wise Breakdown** - Groups and jobs per date
- 🏢 **Company Analytics** - Extracted company information
- ⭐ **Best Jobs Ranking** - Sorted by verification score
- 🔍 **Advanced Filtering** - Tech/Non-Tech/Freelance tabs
- 📝 **Message Viewer** - Read full job descriptions
- 🔄 **Auto-refresh** - Updates every 5 minutes

---

## 🗂️ **File Organization**

### **Source Code** (`src/`)
- `core/` - Telegram client logic
- `services/` - AI classification & verification
- `storage/` - Database & CSV handlers
- `utils/` - Logging & helpers

### **Scripts** (`scripts/`)
- `main.py` - 30-day continuous run
- `daily_run.py` - Daily manual run
- `quick_test.py` - 10-minute test mode
- `check_status.py` - Status monitoring
- `view_dashboard.py` - Terminal UI

### **Dashboard** (`dashboard/`)
- `app.py` - Flask web application
- `templates/` - HTML templates
- `static/` - CSS/JS files

### **Configuration** (`config/`)
- `settings.py` - Main settings
- `config_template.py` - Template for credentials
- `config_moderate.py` - Moderate rate limits

### **Documentation** (`docs/`)
- 20+ comprehensive guides
- Hindi translations
- Safety guidelines
- Quick start guides

---

## 💻 **Usage Examples**

### **Daily Workflow**

```bash
# Morning: Collect data (2-3 hours)
python3 scripts/daily_run.py

# Afternoon: View results
python3 dashboard/app.py
# Browser: http://localhost:7000
```

### **Quick Test** (First time)

```bash
# 10-minute test
python3 scripts/quick_test.py

# Check results
python3 scripts/check_status.py
```

### **Continuous Run** (30 days)

```bash
# Requires laptop to stay ON
python3 scripts/main.py
```

---

## 📊 **Data Access**

### **Database** (SQLite)

```bash
sqlite3 data/database/telegram_jobs.db

SELECT COUNT(*) FROM tech_jobs;
SELECT * FROM tech_jobs WHERE is_verified = 1 LIMIT 10;
```

### **CSV Files** (Excel)

```
data/csv/tech_jobs.csv
data/csv/non_tech_jobs.csv
data/csv/freelance_jobs.csv
```

### **Web API** (JSON)

```
http://localhost:7000/api/stats
http://localhost:7000/api/daily_stats
http://localhost:7000/api/best_jobs
```

---

## 🔧 **Configuration**

### **Setup Your Credentials**

1. Copy template:
   ```bash
   cp config/config_template.py config/config.py
   ```

2. Edit `config/config.py`:
   - Add your API ID and Hash from https://my.telegram.org
   - Add your phone numbers
   
3. Never commit `config/config.py` (already in .gitignore)

### **Adjust Rate Limits**

Edit `config/settings.py` if needed (⚠️ Be careful!)

---

## 🛡️ **Security**

### **Protected Files** (Not in Git)

- ❌ `config/config.py` - API credentials
- ❌ `sessions/*.session` - Login sessions
- ❌ `data/database/*.db` - Your collected data
- ❌ `data/csv/*.csv` - Export files
- ❌ `logs/*.log` - Application logs

### **Safe to Commit**

- ✅ All source code
- ✅ Documentation
- ✅ Templates & config templates
- ✅ Shell scripts
- ✅ data.json (groups list)

---

## 📚 **Documentation**

| File | Description |
|------|-------------|
| `docs/QUICKSTART.md` | 5-minute quick guide |
| `docs/HINDI_SUMMARY.md` | Complete Hindi guide |
| `docs/SAFETY_GUIDE.md` | Account safety tips |
| `docs/DAILY_WORKFLOW.md` | Daily usage guide |
| `docs/UI_GUIDE.md` | Dashboard guide |

---

## 🧪 **Testing**

```bash
# System verification
python3 scripts/test_system.py

# Quick functionality test
python3 scripts/quick_test.py

# Check authorization
python3 scripts/check_auth.py
```

---

## 📈 **Monitoring**

### **Real-time Logs**

```bash
tail -f logs/telegram_client_*.log
```

### **Status Dashboard**

```bash
python3 scripts/check_status.py
```

### **Web Dashboard**

```bash
python3 dashboard/app.py
# http://localhost:7000
```

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📝 **License**

MIT License - Use responsibly and ethically.

---

## ⚠️ **Disclaimer**

- Use dedicated Telegram accounts (not personal)
- Respect Telegram's Terms of Service
- Follow rate limits to avoid bans
- Use for educational/personal purposes only
- Don't spam or abuse automation

---

## 💡 **Support**

- 📖 Check `docs/` folder for detailed guides
- 🐛 Issues: Create GitHub issue
- 💬 Questions: Check documentation first
- 🔒 Security: Never share API keys or sessions

---

## 🎯 **Project Stats**

- **Lines of Code:** 14,835+
- **Files:** 47+
- **Documentation:** 20+ guides
- **Supported Groups:** 857+
- **Languages:** Python, HTML, CSS, JavaScript
- **Database Tables:** 7
- **Safety Features:** 10+

---

**Made with ❤️ for Job Seekers**

**Start collecting jobs today! 🚀**
