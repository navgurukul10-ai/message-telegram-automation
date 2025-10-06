# 📱 Account Authorization Guide

## ✅ Problem Solved! अब OTP Prompt आएगा

पुरानी invalid session files delete कर दी गई हैं। अब fresh authorization करना है।

---

## 🔐 Step-by-Step Authorization Process

### Step 1: Terminal में ये command run करो

```bash
python3 main.py --auth
```

### Step 2: क्या होगा?

System हर account के लिए ये करेगा:

```
1. Checking Account 1 (+919794670665)...
   ℹ️  Code sent to +919794670665
   📱 Please check your Telegram app
   
   Enter the code for Account 1 (+919794670665): _____
                                                  ⬆️ यहाँ OTP डालो
```

### Step 3: OTP कहाँ से आएगा?

1. **Telegram App खोलो** उसी phone number पर
2. **Login code मिलेगा** (5 digit code)
3. **Terminal में enter करो**

### Step 4: सभी 4 Accounts के लिए Repeat

```
Account 1: Enter code → Done ✅
Account 2: Enter code → Done ✅
Account 3: Enter code → Done ✅
Account 4: Enter code → Done ✅
```

---

## 💡 Important Points

### ⚠️ अगर OTP नहीं आ रहा:

1. **Check:** Phone number सही है?
2. **Check:** Telegram app उसी number पर logged in है?
3. **Check:** Network connection ठीक है?
4. **Try:** Code resend करवाओ (wait करो 60 seconds)

### ⚠️ अगर Wrong Code Error:

```
Error: The provided code is invalid
```

**Solution:**
- Code फिर से carefully देखो
- Spaces मत डालो
- सिर्फ numbers enter करो

### ⚠️ अगर Timeout Error:

```
Error: The code has expired
```

**Solution:**
- Script फिर से run करो
- Fresh code आएगा

---

## 🎯 Complete Authorization Example

```bash
$ python3 main.py --auth

============================================================
Telegram Job Fetcher - Starting
============================================================

Initializing Telegram clients...

1. Account 1 (+919794670665)
   ✅ Code sent to +919794670665
   📱 Check your Telegram app
   
   Enter the code for Account 1 (+919794670665): 12345
   ✅ Account 1 authorized successfully!

2. Account 2 (+917398227455)
   ✅ Code sent to +917398227455
   📱 Check your Telegram app
   
   Enter the code for Account 2 (+917398227455): 67890
   ✅ Account 2 authorized successfully!

3. Account 3 (+919140057096)
   ✅ Code sent to +919140057096
   📱 Check your Telegram app
   
   Enter the code for Account 3 (+919140057096): 11223
   ✅ Account 3 authorized successfully!

4. Account 4 (+917828629905)
   ✅ Code sent to +917828629905
   📱 Check your Telegram app
   
   Enter the code for Account 4 (+917828629905): 44556
   ✅ Account 4 authorized successfully!

============================================================
All accounts authorized successfully!
Authorization mode complete.
Restart without --auth flag to start fetching.
============================================================
```

---

## ✅ Authorization Complete होने के बाद

### Check करो सब authorized हैं:

```bash
python3 check_auth.py
```

**Output दिखना चाहिए:**
```
1. Account 1 (+919794670665)
   ✅ AUTHORIZED
   📱 Name: Your Name
   
2. Account 2 (+917398227455)
   ✅ AUTHORIZED
   📱 Name: Your Name
   
... (सभी 4 accounts ✅)
```

---

## 🚀 अब Main Script चलाओ

```bash
python3 main.py
```

**System start हो जाएगा:**
```
Starting continuous fetching for 30 days...
✅ System is running!
```

---

## 🔧 Troubleshooting

### Problem 1: "Code sent" दिख रहा पर prompt नहीं आ रहा

**Solution:**
```bash
# Kill any running process
pkill -f "python3 main.py"

# Clear sessions
rm sessions/*.session

# Try again
python3 main.py --auth
```

### Problem 2: API Error

```
Error: API ID or Hash is invalid
```

**Check:**
- config.py में api_id और api_hash सही हैं?
- https://my.telegram.org से verify करो

### Problem 3: Phone Number Error

```
Error: The phone number is invalid
```

**Check:**
- Format: +91XXXXXXXXXX (country code के साथ)
- Telegram account उस number पर exists करता है?

---

## 📝 Session Files

Authorization complete होने के बाद ये files बनेंगी:

```
sessions/
  ├── session_account1.session  ✅
  ├── session_account2.session  ✅
  ├── session_account3.session  ✅
  └── session_account4.session  ✅
```

**Important:** 
- ये files **मत delete करो**
- बार-बार authorize नहीं करना पड़ेगा
- ये files safe रखो

---

## 🎯 Quick Commands Reference

```bash
# Check authorization status
python3 check_auth.py

# Authorize accounts (first time or re-authorize)
python3 main.py --auth

# Start fetching (after authorization)
python3 main.py

# Check system status (while running)
python3 check_status.py

# View live logs
tail -f logs/main_*.log
```

---

## ✨ Summary

1. **Delete old sessions:** ✅ Done
2. **Run authorization:** `python3 main.py --auth`
3. **Enter OTP codes:** जब prompt आए
4. **Verify:** `python3 check_auth.py`
5. **Start system:** `python3 main.py`

**अब OTP prompt ज़रूर आएगा! 🎉**

