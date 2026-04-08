import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from differ import format_diff_preview
from dotenv import load_dotenv

load_dotenv()


def send_alert(url, classification, diff, site_config=None):
    """
    Send email alert for detected changes.
    
    Args:
        url: Website URL
        classification: 'major', 'minor', or 'none'
        diff: List of changed lines
        site_config: Optional dict with per-site email settings
    """
    preview = format_diff_preview(diff, max_lines=30)

    subject = f"[{classification.upper()}] Change detected: {url}"
    body = f"""
Website Monitor Alert
=====================
URL              : {url}
Classification   : {classification.upper()}

Changes Detected:
-----------------
{preview}

--
Sent by your Website Monitor
"""

    # Always print to terminal
    print(f"\n{'='*55}")
    print(f"  ALERT [{classification.upper()}]: {url}")
    print(f"{'='*55}")
    print(preview)
    print(f"{'='*55}\n")

    # Check if alerts are enabled globally
    alerts_enabled = os.getenv("ALERTS_ENABLED", "true").lower() == "true"
    if not alerts_enabled:
        print("  (Email skipped — ALERTS_ENABLED=false in .env)\n")
        return

    # Get SMTP configuration (prefer per-site, fall back to default)
    enable_custom_smtp = os.getenv("ENABLE_CUSTOM_SMTP", "false").lower() == "true"
    
    if enable_custom_smtp and site_config and "smtp_user" in site_config:
        # Use per-site SMTP credentials
        smtp_user = site_config.get("smtp_user")
        smtp_pass = site_config.get("smtp_pass")
        alert_from = site_config.get("smtp_user")  # Use SMTP user as sender
    else:
        # Use default SMTP credentials
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        alert_from = os.getenv("ALERT_FROM")

    # Get alert recipients (prefer per-site, fall back to default)
    if site_config and "alert_email" in site_config:
        alert_to = site_config.get("alert_email")
    else:
        alert_to = os.getenv("ALERT_TO")

    # Handle multiple recipients (comma-separated)
    recipients = [e.strip() for e in alert_to.split(",")]

    if not all([smtp_user, smtp_pass, alert_from, alert_to]):
        print("  (Email skipped — add credentials to .env to enable)\n")
        return

    try:
        # Get SMTP server config
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

        # Send via SMTP - create fresh message for each recipient to avoid duplicate headers
        if smtp_port == 465:
            # Use SSL
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(smtp_user, smtp_pass)
                for recipient in recipients:
                    msg = MIMEMultipart()
                    msg["Subject"] = subject
                    msg["From"] = alert_from
                    msg["To"] = recipient
                    msg.attach(MIMEText(body, "plain"))
                    smtp.send_message(msg)
        else:
            # Use TLS
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                if smtp_use_tls:
                    smtp.starttls()
                smtp.login(smtp_user, smtp_pass)
                for recipient in recipients:
                    msg = MIMEMultipart()
                    msg["Subject"] = subject
                    msg["From"] = alert_from
                    msg["To"] = recipient
                    msg.attach(MIMEText(body, "plain"))
                    smtp.send_message(msg)

        if len(recipients) == 1:
            print(f"  ✅ Email sent to {recipients[0]}\n")
        else:
            print(f"  ✅ Email sent to {len(recipients)} recipients: {', '.join(recipients)}\n")

    except smtplib.SMTPAuthenticationError:
        print(f"  ❌ ERROR: SMTP login failed for user '{smtp_user}'")
        print(f"  SMTP Server: {smtp_server}:{smtp_port}")
        print("  Fix: Verify SMTP_USER and SMTP_PASS in .env file")
        print("  Gmail users: Use an App Password, not your real password")
        print("  Get App Password: https://myaccount.google.com/apppasswords\n")

    except smtplib.SMTPException as e:
        print(f"  ERROR: Failed to send email — {e}\n")

    except Exception as e:
        print(f"  ERROR: Unexpected error — {e}\n")
if __name__ == "__main__":
    test_diff = [
        "+new pricing: $49/month",
        "-old pricing: $29/month",
        "+added enterprise tier"
    ]

    send_alert("https://example.com/pricing", "major", test_diff)