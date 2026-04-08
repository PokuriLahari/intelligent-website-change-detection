# 🚀 Quick Start Guide - Website Monitor

Get your website monitoring system running in **2 minutes**!

## Step 1: Prepare Email Credentials (2 min)

### Option A: Using Gmail (Recommended)

1. Go to: https://myaccount.google.com/apppasswords

2. Choose **Mail** and **Windows** (or your device)

3. Copy the **16-character password** that appears

4. Edit `.env` file:
```
SMTP_USER=your-email@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx   ← Paste here
ALERT_FROM=your-email@gmail.com
ALERT_TO=your-email@gmail.com   ← Where to send emails
```

### Option B: Using Other Email Providers

See README.md for Outlook, Yahoo, and other providers.

---

## Step 2: Start the Server (30 seconds)

### Windows
Double-click: **RUN.bat**

Or in Command Prompt:
```bash
python app.py
```

### Linux/Mac
```bash
python app.py
```

**Expected Output:**
```
🚀 Server running at http://127.0.0.1:5000
```

---

## Step 3: Open Dashboard (30 seconds)

Open your browser and go to:
```
http://localhost:5000
```

You'll see the WatchDog dashboard! ✅

---

## Step 4: Add Your First Site (1 min)

1. Click **"+ Add Site"** (top right)

2. Paste a website URL:
   ```
   https://example.com
   ```

3. Choose check interval (start with 30 min)

4. Click **"Add Site"**

5. The site now appears in your dashboard

---

## Step 5: Run Your First Check (30 seconds)

1. Click the **↻ icon** next to your site

2. Wait 10-20 seconds for it to complete

3. A first snapshot is saved! 📸

---

## Now What?

### Test Email Alerts

1. Add a **news website** or **product page**:
   - `https://news.ycombinator.com`
   - `https://www.producthunt.com`

2. Set check interval to **5 minutes**

3. Wait for the next check

4. When changes are detected, **check your email**! 📧

### Monitor Multiple Sites

Add as many sites as you want:
- News sites for breaking stories
- Product pages for price changes
- Competitor websites for feature updates
- Job boards for openings
- Stock market pages for ticker changes

---

## 💡 Pro Tips

### Best Websites to Monitor

✅ **Frequently changing:**
- News sites (CNN, BBC, HN)
- E-commerce (Amazon, eBay)
- Job boards (LinkedIn, Indeed)
- Tech news (TechCrunch, Product Hunt)

❌ **Won't work well:**
- Heavy JavaScript sites (React SPAs)
- Paywalled content
- Dynamically loaded pages

### Schedule Tips

| What | Interval |
|------|----------|
| Breaking news | 5 min |
| Job postings | 30 min |
| Sales/deals | 1-2 hours |
| Blog updates | Once daily |

### Email Tips

- Gmail accounts get App Passwords first try
- Check **Spam** folder if email doesn't arrive
- Test with your own email first
- Use comma-separated emails for multiple recipients

---

## 🆘 Troubleshooting

### "Server offline" in Dashboard
- Make sure `python app.py` is still running
- Try refreshing the page
- Check terminal for errors

### Email alerts not arriving
1. Check `.env` file has correct password
2. Verify you're using an **App Password** (not regular password)
3. Check email spam folder
4. Check terminal for error messages

### Website check timing out
- Some sites are slow or block automated requests
- Try adding it anyway - retry after 10 minutes
- Use a VPN if requests are blocked

---

## 🎯 Next Steps

Now that it's running:

1. **Read README.md** for full documentation
2. **Check DEPLOYMENT.md** for production setup
3. **Review alerts.py** to customize email format
4. **Set up auto-start** (optional, see README)

---

## ✅ You're Ready!

Your website monitor is now:
- ✅ Running and monitoring
- ✅ Sending email alerts
- ✅ Saving snapshots locally
- ✅ Tracking change history

## Happy Monitoring! 🐕

Go back to dashboard: **http://localhost:5000**
