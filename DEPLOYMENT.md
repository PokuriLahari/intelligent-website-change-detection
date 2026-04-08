# 🚀 Website Monitor - Deployment Checklist

## Pre-Launch Verification

### ✅ System Requirements
- [x] Python 3.8+ installed
- [x] pip package manager working
- [x] Git (optional, for version control)
- [x] Email account available (Gmail recommended)

### ✅ Installation & Setup
- [x] Dependencies installed via `pip install -r requirements.txt`
- [x] `.env` file created with email credentials
- [x] Email provider configured (Gmail App Password)
- [x] All Python files compile without syntax errors

### ✅ Code Quality
- [x] No AWS/boto3 dependencies remaining
- [x] Local JSON storage configured
- [x] Email alerts integrated
- [x] Database functions working
- [x] API endpoints functioning

### ✅ Files Present
- [x] app.py - Main Flask server
- [x] fetcher.py - Website content retrieval
- [x] differ.py - Change detection
- [x] alerts.py - Email notifications
- [x] monitor.py - CLI monitoring tool
- [x] requirements.txt - Dependencies
- [x] templates/index.html - Web dashboard
- [x] .env.example - Config template
- [x] .env - Email credentials (gitignored)
- [x] README.md - Full documentation
- [x] RUN.bat - Windows startup script

### ✅ Data & Storage
- [x] data/ directory created
- [x] snapshots/ directory created
- [x] sites.json initialized
- [x] history.json initialized

### ✅ Functionality Tests
- [x] App imports successfully
- [x] All database functions working
- [x] JSON file operations working
- [x] Email module configured
- [x] Change detection logic in place

### ✅ Security
- [x] `.env` file in `.gitignore`
- [x] No hardcoded credentials in code
- [x] No AWS keys/tokens exposed
- [x] Email password not logged

---

## 🎯 Launch Procedure

### Step 1: Verify .env Configuration
```bash
# Check that .env has these values:
cat .env
```

**Required variables:**
- SMTP_USER=your-email@gmail.com
- SMTP_PASS=xxxx xxxx xxxx xxxx (App Password)
- ALERT_FROM=your-email@gmail.com
- ALERT_TO=recipient@gmail.com

### Step 2: Start the Server

**Windows:**
```bash
RUN.bat
```

**Linux/Mac:**
```bash
python app.py
```

**Expected output:**
```
🚀 Server running at http://127.0.0.1:5000
```

### Step 3: Access Dashboard
Open browser: **http://localhost:5000**

### Step 4: Add Your First Site

1. Click **"+ Add Site"**
2. Enter URL: `https://example.com`
3. Check interval: `30 minutes`
4. Click **"Add Site"**
5. Click ↻ icon to run first check

### Step 5: Test Email Alerts

1. Add a website with frequent changes (e.g., news site)
2. Set check interval to 2-5 minutes
3. Wait for next check
4. If change detected, check email inbox
5. Verify email received with change summary

---

## 🚨 Troubleshooting Checklist

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| "Server offline" | Make sure `python app.py` is running |
| Email not sending | Check `.env` credentials, verify App Password |
| Port 5000 in use | Kill other processes or change port in app.py |
| Snapshots not saving | Check `snapshots/` folder permissions |
| Website blocked | Try VPN or increase timeouts in fetcher.py |

---

## 🎉 Deployment Success Indicators

✅ **App Running**
- Server starts without errors
- No exceptions in terminal

✅ **Dashboard Loading**
- Web interface loads at http://localhost:5000
- Stats showing correctly

✅ **Site Monitoring**
- Can add sites successfully
- Manual checks run without errors
- Snapshots saved to `snapshots/` folder

✅ **Email Alerts**
- Email received when major/minor change detected
- Email contains proper formatting and change details

✅ **Data Persistence**
- Sites list saved in `data/sites.json`
- Change history saved in `data/history.json`
- Snapshots visible in `snapshots/` folder

---

## 📦 Distribution Package

To share this project:

1. **Exclude these files** (already in .gitignore):
   - `.env` (never share credentials!)
   - `data/` folder (user data)
   - `snapshots/` folder (user data)
   - `.venv/` or virtual environment
   - `__pycache__/`

2. **Include these files:**
   - All `.py` source files
   - `requirements.txt`
   - `.env.example` (template)
   - `README.md` (documentation)
   - `RUN.bat` (Windows launcher)
   - `templates/` folder

3. **Distribution zip** should contain:
   ```
   website-monitor/
   ├── *.py files
   ├── requirements.txt
   ├── .env.example
   ├── README.md
   ├── RUN.bat
   └── templates/
   ```

---

## ✨ Ready for Production?

Before deploying to production:

1. **Performance Test**: Monitor 10+ sites for 1 hour
2. **Memory Usage**: Check RAM usage stays under 200MB
3. **Disk Space**: Verify snapshots don't exceed storage limits
4. **Email Frequency**: Ensure not sending spam emails
5. **Error Handling**: Test with offline websites, network errors
6. **Data Backup**: Copy `data/` folder to safe location

---

## 📞 Support

If deployment fails:
1. Read the full README.md
2. Check terminal error messages
3. Verify all prerequisites installed
4. Ensure .env file has correct values
5. Try restarting Python and clearing cache

**Status: ✅ READY FOR DEPLOYMENT**

Last verified: April 6, 2026
