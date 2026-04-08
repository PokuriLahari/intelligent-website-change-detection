# Email Routing Bug - FIXED ✅

## Summary
The Website Monitor's per-user email routing feature is now fully working. Alerts are correctly sent to each user's configured email address instead of the default shared account.

## What Was Fixed

### The Bug
- **Symptom**: All alerts went to `pokurilahari16@gmail.com` (default email) regardless of per-site configuration
- **Root Cause**: MIME message headers were being duplicated in the email construction loop
  - Code set `msg["To"] = ", ".join(recipients)` once
  - Then in the loop set `msg["To"] = recipient` multiple times
  - MIME messages append headers instead of replacing, creating multiple To headers
  - Gmail rejected with: "RFC 5322 violation - multiple To headers"

### The Solution
Modified [alerts.py](alerts.py) to create a **fresh MIMEMultipart message for each recipient** instead of reusing one message object.

**Before (broken)**:
```python
msg = MIMEMultipart()
msg["To"] = ", ".join(recipients)  # Sets To header once
for recipient in recipients:
    msg["To"] = recipient  # Adds duplicate To header each iteration! ❌
    smtp.send_message(msg)
```

**After (fixed)**:
```python
for recipient in recipients:
    msg = MIMEMultipart()  # Fresh message for each recipient ✅
    msg["Subject"] = subject
    msg["From"] = alert_from
    msg["To"] = recipient  # Single To header per message
    msg.attach(MIMEText(body, "plain"))
    smtp.send_message(msg)
```

## Verification Results

All 6 monitored sites now correctly route alerts to their configured email addresses:

| Site | URL | Configured Email | Status |
|------|-----|------------------|--------|
| 1 | openai.com/pricing | pokurilahari16@gmail.com | ✅ Verified |
| 2 | anthropic.com/news | kolludruvitha18@gmail.com | ✅ Verified |
| 3 | aws.amazon.com/pricing | dhruvasai1706@gmail.com | ✅ Verified |
| 4 | vercel.com/pricing | dhruvasai1706@gmail.com | ✅ Verified |
| 5 | news.ycombinator.com | 2420030552@klh.edu.in | ✅ Verified |
| 6 | news.ycombinator.com | dhruvasai1706@gmail.com | ✅ Verified |

## How It Works

1. **Data Layer**: Each site in `data/sites.json` has an `alert_email` field with the user's email
2. **API Layer**: When a check is triggered, `app.py` passes the site configuration to the check function
3. **Alert Layer**: [alerts.py](alerts.py) receives the site_config and selects the correct email:
   - If `site_config` has `alert_email`: **Use it** ✅
   - Otherwise: Fall back to `ALERT_TO` from .env

## Files Modified
- [alerts.py](alerts.py) - Fixed MIME message construction in send_alert() function
- [app.py](app.py) - Passes site_config through run_check() (already correct)

## Deployment Status
✅ **Ready for production** - The email routing feature is fully functional and tested.

No additional configuration needed - existing .env and sites.json are compatible.
