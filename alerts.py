import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from differ import format_diff_preview
from dotenv import load_dotenv

load_dotenv()


# ===================== AWS SES =====================

def send_via_aws_ses(subject, body, alert_from, recipients):
    """
    Send alert email using AWS Simple Email Service (SES).

    Free tier: 62,000 emails/month (when sent from Amazon EC2/Lambda).
    Outside EC2: first 62,000 emails/month free in sandbox, then $0.10/1000.

    Required .env variables:
        AWS_ACCESS_KEY_ID     – IAM user access key
        AWS_SECRET_ACCESS_KEY – IAM user secret key
        AWS_REGION            – e.g. us-east-1
        ALERT_FROM            – verified sender email address
    """
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        print("  ❌ boto3 not installed. Run: pip install boto3\n")
        return False

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not all([aws_access_key, aws_secret_key]):
        print("  (AWS SES skipped — AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY not set)\n")
        return False

    try:
        client = boto3.client(
            "ses",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

        for recipient in recipients:
            client.send_email(
                Source=alert_from,
                Destination={"ToAddresses": [recipient]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
                },
            )

        if len(recipients) == 1:
            print(f"  ✅ AWS SES email sent to {recipients[0]}\n")
        else:
            print(f"  ✅ AWS SES email sent to {len(recipients)} recipients\n")
        return True

    except (BotoCoreError, ClientError) as e:
        print(f"  ❌ AWS SES error: {e}\n")
        return False
    except Exception as e:
        print(f"  ❌ AWS SES unexpected error: {e}\n")
        return False


# ===================== AWS SNS =====================

def send_via_aws_sns(subject, body):
    """
    Publish a change-detection notification to an AWS SNS topic.

    Free tier: 1 million SNS notifications/month forever.

    Required .env variables:
        AWS_ACCESS_KEY_ID     – IAM user access key
        AWS_SECRET_ACCESS_KEY – IAM user secret key
        AWS_REGION            – e.g. us-east-1
        AWS_SNS_TOPIC_ARN     – full ARN of your SNS topic
    """
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        print("  ❌ boto3 not installed. Run: pip install boto3\n")
        return False

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    sns_topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")

    if not all([aws_access_key, aws_secret_key, sns_topic_arn]):
        print("  (AWS SNS skipped — AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SNS_TOPIC_ARN not set)\n")
        return False

    try:
        client = boto3.client(
            "sns",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

        if len(subject) > 100:
            print(f"  ⚠ SNS subject truncated from {len(subject)} to 100 chars\n")
        client.publish(
            TopicArn=sns_topic_arn,
            Subject=subject[:100],
            Message=body,
        )

        print(f"  ✅ AWS SNS notification published to topic\n")
        return True

    except (BotoCoreError, ClientError) as e:
        print(f"  ❌ AWS SNS error: {e}\n")
        return False
    except Exception as e:
        print(f"  ❌ AWS SNS unexpected error: {e}\n")
        return False


# ===================== Azure Communication Services =====================

def send_via_azure_email(subject, body, alert_from, recipients):
    """
    Send alert email using Azure Communication Services (Email).

    Free tier: 100 emails/day on Azure Free account.

    Required .env variables:
        AZURE_COMMUNICATION_CONNECTION_STRING – connection string from Azure portal
        ALERT_FROM                            – verified sender address (DoNotReply@<domain>)
    """
    try:
        from azure.communication.email import EmailClient
    except ImportError:
        print("  ❌ azure-communication-email not installed. Run: pip install azure-communication-email\n")
        return False

    connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")

    if not connection_string:
        print("  (Azure Email skipped — AZURE_COMMUNICATION_CONNECTION_STRING not set)\n")
        return False

    try:
        client = EmailClient.from_connection_string(connection_string)

        to_recipients = [{"address": r} for r in recipients]

        message = {
            "senderAddress": alert_from,
            "recipients": {"to": to_recipients},
            "content": {
                "subject": subject,
                "plainText": body,
            },
        }

        poller = client.begin_send(message)
        result = poller.result()

        if result.get("status") == "Succeeded":
            print(f"  ✅ Azure email sent successfully\n")
        else:
            print(f"  ✅ Azure email dispatched (status: {result.get('status', 'unknown')})\n")
        return True

    except Exception as e:
        print(f"  ❌ Azure Communication Services error: {e}\n")
        return False


# ===================== Main alert dispatcher =====================

def send_alert(url, classification, diff, site_config=None):
    """
    Send email alert for detected changes.

    Dispatch order (first configured provider wins):
      1. AWS SES   — set ALERT_PROVIDER=aws_ses
      2. AWS SNS   — set ALERT_PROVIDER=aws_sns
      3. Azure     — set ALERT_PROVIDER=azure
      4. SMTP      — default (Gmail / any SMTP server)

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

    # Determine alert provider
    alert_provider = os.getenv("ALERT_PROVIDER", "smtp").lower()

    # Get alert recipients (prefer per-site, fall back to default)
    if site_config and "alert_email" in site_config:
        alert_to = site_config.get("alert_email")
    else:
        alert_to = os.getenv("ALERT_TO", "")

    alert_from = os.getenv("ALERT_FROM", "")
    recipients = [e.strip() for e in alert_to.split(",") if e.strip()]

    # ── AWS SES ──────────────────────────────────────────────
    if alert_provider == "aws_ses":
        if not recipients or not alert_from:
            print("  (AWS SES skipped — ALERT_FROM / ALERT_TO not set)\n")
            return
        send_via_aws_ses(subject, body, alert_from, recipients)
        return

    # ── AWS SNS ──────────────────────────────────────────────
    if alert_provider == "aws_sns":
        send_via_aws_sns(subject, body)
        return

    # ── Azure Communication Services ─────────────────────────
    if alert_provider == "azure":
        if not recipients or not alert_from:
            print("  (Azure Email skipped — ALERT_FROM / ALERT_TO not set)\n")
            return
        send_via_azure_email(subject, body, alert_from, recipients)
        return

    # ── SMTP (default) ────────────────────────────────────────
    _send_via_smtp(subject, body, alert_from, recipients, site_config)


def _send_via_smtp(subject, body, alert_from, recipients, site_config=None):
    """Send alert via SMTP (default / Gmail path)."""

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

    if not all([smtp_user, smtp_pass, alert_from, recipients]):
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