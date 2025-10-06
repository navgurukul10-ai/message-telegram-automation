# 🌐 Web Dashboard - Port 7000

## ✅ **Dashboard Port 7000 पर चलेगा!**

---

## 🚀 **कैसे Start करें:**

### **Method 1: Script से (Easy!)**

```bash
./start_dashboard.sh
```

### **Method 2: Direct Command**

```bash
python3 web_dashboard.py
```

---

## 🌐 **Browser में खोलो:**

```
http://localhost:7000
```

**या**

```
http://127.0.0.1:7000
```

---

## 📊 **Dashboard में क्या दिखेगा:**

### **1. Overall Statistics (Cards):**
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Tech     │  │ Non-Tech │  │ Freelance│
│ 1,234    │  │   567    │  │   890    │
└──────────┘  └──────────┘  └──────────┘

┌──────────┐  ┌──────────┐  ┌──────────┐
│ Groups   │  │ Verified │  │Avg Score │
│  240     │  │  1,845   │  │  78.5%   │
└──────────┘  └──────────┘  └──────────┘
```

### **2. Date-wise Groups Table:**
```
Date          | Groups | Group Names
────────────────────────────────────────────
2025-01-08    |   8    | TechJobs, PythonDev, DevOps, ...
2025-01-07    |   8    | AIJobs, RemoteWork, ...
2025-01-06    |   8    | CloudJobs, SecurityJobs, ...
```

### **3. Date-wise Jobs Table:**
```
Date          | Tech | Non-Tech | Freelance | Total
───────────────────────────────────────────────────
2025-01-08    |  45  |    23    |    32     |  100
2025-01-07    |  52  |    18    |    27     |   97
2025-01-06    |  38  |    25    |    31     |   94
```

### **4. Best Jobs (Interactive!):**
```
[Tabs]  [Best Jobs] [Tech Jobs] [Non-Tech] [Freelance]

Google India                              ⭐ 95.5%
─────────────────────────────────────────────────────
Senior Python Developer needed...

Skills: Python, Django, AWS
Salary: ₹20-30 LPA
Mode: Remote
Date: 2025-01-08
Group: TechJobs India

[Full Message Text...]
```

**Tabs switch करके देख सकते हो!**

---

## 🎨 **UI Features:**

✅ **Colorful Design** - Purple gradient background
✅ **Hover Effects** - Cards पर hover करो
✅ **Tabs** - Tech/Non-Tech/Freelance switch करो
✅ **Tables** - Sortable, hoverable
✅ **Badges** - Color-coded categories
✅ **Responsive** - Mobile पर भी देख सकते हो
✅ **Auto-refresh** - हर 5 मिनट में update
✅ **Refresh Button** - Manual refresh भी कर सकते हो

---

## 🔄 **Real-time Updates:**

```
Dashboard running...
  ↓
Daily script चलाओ (दूसरे terminal में)
  ↓
New data save होगा
  ↓
Dashboard में automatically update (5 min में)
  ↓
या Refresh button click करो (instant update!)
```

---

## 💻 **Complete Workflow:**

### **Terminal 1: Data Collection**
```bash
python3 daily_run.py

Output:
[10:00] Starting...
[10:05] Joining groups...
[10:35] Fetching messages...
[12:30] Done! 8 groups, 100 jobs
```

### **Terminal 2: Dashboard**
```bash
python3 web_dashboard.py

Output:
Starting Web Dashboard
Dashboard will open at: http://localhost:7000

 * Running on http://0.0.0.0:7000
```

### **Browser:**
```
Open: http://localhost:7000

[Beautiful UI दिखेगा]
- Date-wise data
- Groups info
- Jobs breakdown
- Best jobs
- Messages
```

---

## 🎯 **Daily Checklist:**

### Morning (10 AM):
```bash
[ ] Laptop ON करो
[ ] Terminal खोलो
[ ] python3 daily_run.py चलाओ
[ ] 2-3 घंटे चलने दो
```

### Afternoon (1 PM):
```bash
[ ] python3 web_dashboard.py चलाओ
[ ] Browser: http://localhost:7000
[ ] Date-wise data देखो
[ ] Best jobs check करो
[ ] CSV download करो (optional)
```

### Evening:
```bash
[ ] Dashboard बंद करो (Ctrl+C)
[ ] Laptop बंद कर सकते हो ✅
```

---

## 📱 **Mobile पर भी देख सकते हो:**

अगर laptop और mobile same WiFi पर हैं:

```bash
# Find laptop IP
ip addr show | grep "inet "

# Example IP: 192.168.1.100

# Mobile browser में खोलो:
http://192.168.1.100:7000
```

**UI responsive है, mobile पर भी अच्छा दिखेगा!** 📱

---

## 🛑 **Dashboard बंद करने के लिए:**

```
Terminal में:
Press Ctrl + C

Output:
✅ Dashboard stopped
```

---

## 💡 **Pro Tips:**

### **1. Bookmark करो:**
```
Browser में bookmark:
http://localhost:7000
```

### **2. Dual Monitor:**
```
Screen 1: Daily script running
Screen 2: Dashboard open
```

### **3. Export Data:**
```
CSV files:
data/csv/tech_jobs.csv → Excel में खोलो
```

---

## ✨ **Summary:**

### **आपको मिलेगा Port 7000 पर:**

✅ **Date-wise Groups** - टेबल में
✅ **Date-wise Jobs Count** - Tech/Non-Tech/Freelance
✅ **Best Jobs** - Verification score के साथ
✅ **Full Messages** - पूरा text readable
✅ **Company Info** - Name, website, salary, skills
✅ **Beautiful UI** - Modern, colorful
✅ **Auto-refresh** - हर 5 मिनट
✅ **Tabs** - Category switch करने के लिए

---

## 🚀 **अभी Start करो:**

```bash
# Dashboard start करो
python3 web_dashboard.py

# Browser में खोलो
http://localhost:7000
```

**Beautiful UI दिखेगा! 🎨✨**

*Note: अभी database खाली होगा। पहले `daily_run.py` चलाओ data collect करने के लिए!*

