# 🤖 Auto Apply System - Setup Guide

## ✨ Overview

Automatic job application system for Gaurav Rajput (DevOps Engineer)

**Features:**
- ✅ Automatically extract job application links from database
- ✅ Filter jobs based on skills and preferences
- ✅ Send email applications with resume
- ✅ Auto CC to laxmiyadav21@navgurukul.org
- ✅ Track all applications in database
- ✅ Daily application limits
- ✅ Dry-run mode for testing

---

## 📋 Prerequisites

1. **Gmail Account** (gx1b2j@gmail.com)
2. **App-Specific Password** for Gmail
3. **Resume PDF** file
4. **Python 3.7+**

---

## 🔧 Setup Steps

### Step 1: Enable Gmail App Password

1. Go to Google Account: https://myaccount.google.com/
2. Security → 2-Step Verification (enable if not already)
3. App passwords → Select app: "Mail", device: "Other" → "Auto Apply"
4. Copy the 16-character password

### Step 2: Configure Email Credentials

**Option A: Environment Variable (Recommended)**
```bash
export EMAIL_APP_PASSWORD="your-16-char-password-here"
```

Add to `~/.bashrc` or `~/.zshrc` for permanent:
```bash
echo 'export EMAIL_APP_PASSWORD="your-password"' >> ~/.bashrc
source ~/.bashrc
```

**Option B: Config File**
```bash
cd /home/navgurukul/simul_automation
cp config/email_config.example.json config/email_config.json
# Edit config/email_config.json and add your password
```

### Step 3: Add Your Resume

```bash
# Copy your resume PDF
cp /path/to/your/Gaurav_Rajput_DevOps.pdf resume/

# Or create a symbolic link
ln -s /path/to/your/resume.pdf resume/Gaurav_Rajput_DevOps.pdf
```

### Step 4: Verify Profile

Edit `config/gaurav_profile.json` if needed:
- Update email, phone
- Add/remove skills
- Adjust preferences
- Set daily application limits

---

## 🚀 Usage

### Test Run (Dry Run - No Emails Sent)

```bash
python3 auto_apply.py --dry-run
```

This will:
- Extract jobs from database
- Filter based on profile
- Show what emails WOULD be sent
- NO actual emails sent

### Live Run (Send Emails)

```bash
python3 auto_apply.py
```

### Advanced Options

```bash
# Apply to last 3 days of jobs only
python3 auto_apply.py --days 3

# Increase minimum match score to 50%
python3 auto_apply.py --min-match-score 50

# Email applications only (skip LinkedIn, etc.)
python3 auto_apply.py --email-only

# Maximum 5 applications per day
python3 auto_apply.py --max-applications 5

# Combined example
python3 auto_apply.py --days 7 --min-match-score 40 --max-applications 10
```

---

## 📊 How It Works

### 1. Job Extraction
- Reads messages from database
- Extracts application links (URLs, emails)
- Categorizes by type: email, LinkedIn, Naukri, Indeed, etc.

### 2. Job Filtering
- Checks skill match (compares job keywords with your skills)
- Verifies role match (DevOps, SRE, Cloud Engineer, etc.)
- Excludes unwanted keywords (junior, fresher, etc.)
- Requires minimum keywords (devops, aws, cloud, etc.)
- Calculates match score (0-100%)

### 3. Email Application
- Generates professional email
- Attaches resume PDF
- Sends to company email
- **Auto CC to laxmiyadav21@navgurukul.org**
- Tracks in database

### 4. Application Tracking
- Stores all applications in database
- Prevents duplicate applications
- Tracks daily limits
- Records match scores

---

## 📧 Email Format

**Subject:**
```
Application for [Job Title from posting]
```

**Body:**
```
Dear Hiring Manager,

I am writing to express my strong interest in the position mentioned in your job posting.

With over 12 years of experience as a DevOps Engineer / Tech Lead, I bring a comprehensive skill set in AWS, Azure, Docker, Kubernetes, Terraform and more.

My expertise includes:
• Cloud Platforms: AWS, Azure, GCP
• Container Orchestration: Docker, Kubernetes, ECS, Nomad
• Infrastructure as Code: Terraform, CloudFormation, Ansible
[...]

Best regards,
Gaurav Rajput
+91 8790470201
gx1b2j@gmail.com
LinkedIn: https://linkedin.com/in/x1b2j
GitHub: https://github.com/x1b2j
```

**Attachments:**
- Gaurav_Rajput_DevOps.pdf

**CC:**
- laxmiyadav21@navgurukul.org

---

## 📈 Daily Workflow

### Recommended Schedule

Run once or twice daily:

```bash
# Morning run (10 AM)
python3 auto_apply.py --days 1 --max-applications 5

# Evening run (6 PM)
python3 auto_apply.py --days 1 --max-applications 5
```

### Automation with Cron

Add to crontab:
```bash
crontab -e

# Add:
0 10 * * * cd /home/navgurukul/simul_automation && /usr/bin/python3 auto_apply.py --max-applications 5 >> logs/auto_apply.log 2>&1
0 18 * * * cd /home/navgurukul/simul_automation && /usr/bin/python3 auto_apply.py --max-applications 5 >> logs/auto_apply.log 2>&1
```

---

## 📊 Check Application Status

```bash
# View all applications
python3 << EOF
from src.auto_apply.tracker import ApplicationTracker
tracker = ApplicationTracker()

stats = tracker.get_stats()
print(f"Total Applications: {stats['total']}")
print(f"Today: {stats['today']}")
print(f"By Type: {stats['by_type']}")
print(f"By Status: {stats['by_status']}")

# Recent applications
recent = tracker.get_applied_jobs(days=7)
for app in recent[:10]:
    print(f"\n{app['job_title']}")
    print(f"  Applied: {app['applied_date']}")
    print(f"  Type: {app['application_type']}")
    print(f"  Match: {app['match_score']}%")
EOF
```

---

## ⚠️ Important Notes

### Rate Limiting
- Default: 10 applications/day
- Adjust with `--max-applications`
- 10 seconds delay between emails

### Email Safety
- Uses app-specific password (not main password)
- Password never stored in code
- SMTP over TLS (secure)

### Application Quality
- Only applies to relevant jobs (30%+ match by default)
- Filters out junior/fresher positions
- Requires DevOps-related keywords

### Legal & Ethical
- Only applies to jobs you're qualified for
- Resume and profile must be accurate
- Be ready to respond to emails/calls

---

## 🔍 Troubleshooting

### "Email password not configured"
```bash
export EMAIL_APP_PASSWORD="your-password"
```

### "Resume not found"
```bash
ls -lh resume/
# Make sure Gaurav_Rajput_DevOps.pdf exists
```

### "No applicable jobs found"
- Check database has jobs: `python3 scripts/check_status.py`
- Reduce days: `--days 30`
- Lower match score: `--min-match-score 20`

### "Already applied to all jobs"
- Wait for new jobs to be fetched
- Run `daily_run.py` to fetch more jobs

---

## 📝 Example Output

```
======================================================================
  🤖 AUTO APPLY SYSTEM
======================================================================

📊 Application Stats:
   • Total applications: 15
   • Applications today: 3

🔍 Step 1: Extracting jobs from last 7 days...
   Found 45 applicable jobs

📋 Jobs by Application Type:
   • email: 12 jobs
   • linkedin: 20 jobs
   • naukri: 8 jobs
   • career_page: 5 jobs

🎯 Step 2: Filtering jobs (min match score: 30.0%)...
   25 jobs match your profile

📧 Step 3: Applying to jobs...
   Mode: LIVE

📧 Job 1: Senior DevOps Engineer - Remote...
   Group: Tech Jobs Occean
   Match Score: 78.5%
   Email: careers@company.com
   ✅ Application sent!
   📋 CC: laxmiyadav21@navgurukul.org
   ⏳ Waiting 10 seconds...

[...]

======================================================================
  ✅ AUTO APPLY COMPLETE
======================================================================

📊 Summary:
   • Applications sent: 7
   • Total today: 10
   • Remaining quota: 0

💡 Check your email for sent applications!
   CC sent to: laxmiyadav21@navgurukul.org
```

---

## 🎯 Next Steps

1. **Test with dry-run first**
2. **Verify email credentials**
3. **Add your resume**
4. **Run live with small limit** (--max-applications 2)
5. **Check sent emails**
6. **Increase limits gradually**
7. **Set up cron for automation**

---

## 📞 Support

For issues or questions, contact:
- laxmiyadav21@navgurukul.org

---

**Good luck with your job applications! 🚀**

