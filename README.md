# 🐕 WatchDog - Website Monitor

A powerful, easy-to-use website monitoring system that tracks changes on any website and alerts you via email in real-time.

## ✨ Features

- 🌐 **Monitor Multiple Websites** - Add unlimited URLs to track
- ⏱️ **Flexible Scheduling** - Check sites every 2 minutes to daily
- 📊 **Smart Change Detection** - Classifies changes as Major, Minor, or None
- 📧 **Email Alerts** - Get notified instantly when important changes happen
- 🎨 **Beautiful Dashboard** - Modern, responsive web interface
- 💾 **Local Storage** - No cloud dependency, all data stored locally
- ⚡ **Zero AWS/Cloud** - Runs 100% on your machine

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Gmail account** for sending email alerts (or any SMTP-compatible email)
- **~100MB** disk space for snapshots

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email Alerts

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. **Set up Gmail App Password** (recommended):
   - Go to: https://myaccount.google.com/apppasswords
   - Generate a new App Password for "Mail" on "Windows"
   - Copy the 16-character password

3. Edit `.env` file with your credentials:
```
SMTP_USER=your-email@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx
ALERT_FROM=your-email@gmail.com
ALERT_TO=your-email@gmail.com
```

### 3. Start the Server

```bash
python app.py
```

You'll see:
```
🚀 Server running at http://127.0.0.1:5000
```

### 4. Open Dashboard

Open your browser and go to: **http://localhost:5000**

## 📖 How to Use

### Adding a Site

1. Click **"+ Add Site"** button in top right
2. Paste the website URL (must start with `https://`)
3. Choose check interval (2 min to 1 day)
4. Optionally add alert email and keywords to watch
5. Click **"Add Site"**

### Monitoring

- **Dashboard** - See overview of all sites and recent changes
- **Sites Tab** - Full list with status and last check time
- **History Tab** - Complete log of all detected changes
- **Alerts Tab** - Email configuration and alert activity

### Running Checks

- **Manual Check** - Click the ↻ icon next to any site
- **Check All** - Use the sidebar "Check All Now" button
- **Auto Check** - Runs automatically at your configured interval

## 🎯 Change Classification

The system automatically classifies changes:

| Type | Trigger | Action |
|------|---------|--------|
| 🔴 **Major** | >10% of lines changed OR >20 lines | **Email sent** |
| 🟡 **Minor** | Keywords found OR >3 lines changed | **Email sent** |
| 🟢 **None** | Small cosmetic changes only | No email |

**Keywords checked**: price, $, €, launch, new, removed, update, sale, discount, free, limited

## 📅 Scheduling Guide

| Interval | Best For |
|----------|----------|
| 2-5 min | E-commerce (price changes), breaking news |
| 10-30 min | Job boards, events, competitor sites |
| 1 hour | News feeds, blogs, status pages |
| 1 day | Change logs, documentation, archives |

## 📧 Email Alerts Setup

### Using Gmail (Recommended)

1. [Generate App Password](https://myaccount.google.com/apppasswords)
2. Use it in `.env` as `SMTP_PASS`
3. Restart the app

### Using Other Email Providers

Update `app.py` line 26 in `alerts.py` SMTP server settings:
```python
# Gmail (current)
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

# Outlook
with smtplib.SMTP_SSL("smtp-mail.outlook.com", 587) as smtp:

# Yahoo
with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as smtp:
```

## 📁 Project Structure

```
website-monitor/
├── app.py                 # Main Flask web server
├── fetcher.py            # Website content retriever
├── differ.py             # Change detection & classification
├── alerts.py             # Email notification system
├── monitor.py            # CLI monitoring tool
├── requirements.txt      # Python dependencies
├── .env                  # Email config (keep private!)
├── .env.example         # Config template
├── sites.json           # Saved sites list
├── data/                # Local storage
│   ├── sites.json       # Sites database
│   └── history.json     # Change history
├── snapshots/           # Website snapshots
│   └── [site]_*.json    # Individual snapshots
└── templates/
    └── index.html       # Web dashboard

```

## 🔧 Configuration

### Snapshot Storage

Snapshots are saved in `snapshots/` folder with format:
```
domain_com_20260406_143050.json
```

Each snapshot contains:
- URL monitored
- Timestamp
- Content checksum (SHA-256)
- Full page content

### Data Files

- `data/sites.json` - All monitored URLs and settings
- `data/history.json` - Change detection log

**Backup these files regularly!**

## 🚨 Troubleshooting

### "Server is offline" in Dashboard
- Make sure `python app.py` is running
- Check terminal for error messages
- Verify Flask is listening on port 5000

### Email not sending
- Check `.env` file has correct credentials
- Verify Gmail App Password is being used (not your real password)
- Check internet connection
- Review email logs in terminal for error details

### Snapshots taking too long
- The app waits up to 20 seconds per site
- Check Internet speed with: `curl https://your-url.com`
- Consider increasing check intervals

### Port 5000 already in use
- Change port in `app.py` line 301: `app.run(port=5001)`
- Then access: `http://localhost:5001`

## 💡 Tips & Best Practices

1. **Email Frequency** - Don't set interval below 5 minutes to avoid spam
2. **Keywords** - Add domain-specific keywords (e.g., "out of stock", "breaking")
3. **Multiple Email Alerts** - Modify `.env` for comma-separated recipients
4. **Backup Data** - Copy `data/` folder regularly
5. **Run in Background** - Use `nohup python app.py &` on Linux/Mac
6. **Use VPN** - Some sites block rapid requests; rotate user agents

## 📊 Performance

- **Memory Usage**: ~50-100MB at idle
- **Disk Usage**: ~1MB per snapshot (depends on page size)
- **Network**: ~200KB-2MB per site check
- **CPU**: Minimal when idle, brief spike during checks

Keep oldest snapshots: Delete from `snapshots/` folder when storage fills

## 🔒 Privacy & Security

- ✅ No data sent to cloud services
- ✅ Email credentials stored locally only
- ✅ Add `.env` to `.gitignore` (already done)
- ✅ HTTPS enabled for all checks
- ⚠️ Store `.env` safely - it contains credentials

## 📝 API Reference

### Dashboard Access
```
GET http://localhost:5000/
```

### Get All Sites
```
GET http://localhost:5000/api/sites
```

### Add New Site
```
POST http://localhost:5000/api/sites
Body: {"url": "https://example.com", "interval_minutes": 30}
```

### Get Change History
```
GET http://localhost:5000/api/history
```

### Manual Check
```
POST http://localhost:5000/api/check
Body: {"url": "https://example.com"}
```

## 🐛 Known Issues & Limitations

- JavaScript-heavy sites may not capture all content changes
- Very large pages (>10MB) may timeout
- Some sites block automated requests - use VPN if needed

## 🤝 Support

If you encounter issues:
1. Check the terminal for error messages
2. Review `.env` file configuration
3. Try manual reload: Refresh button on dashboard
4. Restart the app: Stop `python app.py` and run again

## 📄 License

Free to use for personal and commercial purposes.

## 🎉 Ready to Monitor?

```bash
python app.py
```

Then visit: **http://localhost:5000**

Happy monitoring! 🐕
