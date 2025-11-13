# 🚀 AUTO APPLY - QUICK START (3 Minutes Setup)

## ⚡ सिर्फ 3 steps:

### Step 1: Gmail App Password बनाएं (2 minutes)

1. **Google Account खोलें**: https://myaccount.google.com/security
2. **2-Step Verification** enable करें (अगर already नहीं है)
3. **App passwords** पर click करें
4. **Select app**: Mail, **Select device**: Other (Auto Apply)
5. **Generate** करें
6. **16-character password copy करें** (जैसे: `abcd efgh ijkl mnop`)

### Step 2: Password Terminal में set करें

```bash
export EMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
```

*(अपना actual password paste करें ऊपर की quotes में)*

### Step 3: Resume Add करें

```bash
# अपनी resume PDF copy करें
cp /path/to/your/resume.pdf /home/navgurukul/simul_automation/resume/Gaurav_Rajput_DevOps.pdf
```

---

## ✅ अब बस RUN करें:

### Test Run (कोई email नहीं भेजेगा, सिर्फ देखने के लिए):

```bash
cd /home/navgurukul/simul_automation
python3 auto_apply.py --dry-run
```

### Real Run (Emails भेजेगा):

```bash
cd /home/navgurukul/simul_automation
python3 auto_apply.py
```

---

## 🎯 बस इतना ही!

Script automatically:
- ✅ Database से jobs निकालेगी
- ✅ Gaurav की profile से match करेगी  
- ✅ Filtered jobs को email भेजेगी
- ✅ Resume attach करेगी
- ✅ CC में `laxmiyadav21@navgurukul.org` add करेगी
- ✅ Database में track करेगी

---

## 📊 Result देखने के लिए:

```bash
# कितने applications भेजे गए
sqlite3 data/database/telegram_jobs.db "SELECT COUNT(*) FROM applications"

# आज के applications
sqlite3 data/database/telegram_jobs.db "SELECT * FROM applications WHERE DATE(applied_date) = DATE('now')"
```

---

## 🔧 Daily Run करने के लिए:

हर दिन manually run करें या cron में add करें:

```bash
# रोज़ 10 AM और 6 PM
crontab -e

# Add:
0 10 * * * cd /home/navgurukul/simul_automation && python3 auto_apply.py --max-applications 5
0 18 * * * cd /home/navgurukul/simul_automation && python3 auto_apply.py --max-applications 5
```

---

**बस! अब auto-apply ready है! 🎉**

