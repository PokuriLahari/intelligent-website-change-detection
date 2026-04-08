"""
Cloud notification integrations for Website Monitor (WatchDog).

Supported providers (all have free tiers):
  - AWS SNS  : 1,000 email/HTTP notifications per month — always free
  - AWS SES  : 200 emails/day in sandbox; 62,000/month from EC2 — free for 12 months
  - Azure ACS: 100 emails/day — always free

Configure via environment variables in your .env file.
See .env.example for required keys for each provider.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# AWS SNS
# ---------------------------------------------------------------------------

def send_aws_sns(subject, message):
    """
    Publish a notification to an AWS SNS topic.

    Free tier: 1,000 email notifications and 1,000 HTTP/HTTPS deliveries per month.
    Requires: AWS_SNS_TOPIC_ARN, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
    """
    topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not topic_arn:
        return False, "AWS_SNS_TOPIC_ARN not set in .env"

    try:
        import boto3
        client = boto3.client(
            "sns",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        # SNS subject is capped at 100 characters
        response = client.publish(
            TopicArn=topic_arn,
            Subject=subject[:100],
            Message=message,
        )
        return True, response.get("MessageId", "sent")
    except ImportError:
        return False, "boto3 not installed — run: pip install boto3"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# AWS SES
# ---------------------------------------------------------------------------

def send_aws_ses(subject, body, to_addresses, from_address=None):
    """
    Send email via AWS Simple Email Service (SES).

    Free tier: 200 emails/day in sandbox mode; 62,000 emails/month from an EC2 instance.
    Requires: AWS_SES_SENDER_EMAIL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
    Note: In sandbox mode both sender and recipient addresses must be verified in SES console.
    """
    region = os.getenv("AWS_REGION", "us-east-1")
    sender = from_address or os.getenv("AWS_SES_SENDER_EMAIL")

    if not sender:
        return False, "AWS_SES_SENDER_EMAIL not set in .env"

    recipients = to_addresses if isinstance(to_addresses, list) else [to_addresses]
    if not recipients:
        return False, "No recipients specified"

    try:
        import boto3
        client = boto3.client(
            "ses",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        response = client.send_email(
            Source=sender,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        return True, response.get("MessageId", "sent")
    except ImportError:
        return False, "boto3 not installed — run: pip install boto3"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Azure Communication Services (ACS) Email
# ---------------------------------------------------------------------------

def send_azure_acs_email(subject, body, to_addresses, from_address=None):
    """
    Send email via Azure Communication Services Email.

    Free tier: 100 emails/day — always free (no credit card required for this limit).
    Requires: AZURE_COMMUNICATION_CONNECTION_STRING, AZURE_ACS_SENDER_ADDRESS
    The sender address must be a verified domain/address in your ACS resource.
    """
    connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    sender = from_address or os.getenv("AZURE_ACS_SENDER_ADDRESS")

    if not connection_string:
        return False, "AZURE_COMMUNICATION_CONNECTION_STRING not set in .env"
    if not sender:
        return False, "AZURE_ACS_SENDER_ADDRESS not set in .env"

    recipients = to_addresses if isinstance(to_addresses, list) else [to_addresses]
    if not recipients:
        return False, "No recipients specified"

    try:
        from azure.communication.email import EmailClient
        client = EmailClient.from_connection_string(connection_string)
        message = {
            "senderAddress": sender,
            "recipients": {
                "to": [{"address": addr} for addr in recipients]
            },
            "content": {
                "subject": subject,
                "plainText": body,
            },
        }
        poller = client.begin_send(message)
        result = poller.result()
        # OperationResult exposes the ID via the message_id attribute
        msg_id = getattr(result, "message_id", None) or "sent"
        return True, msg_id
    except ImportError:
        return False, "azure-communication-email not installed — run: pip install azure-communication-email"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Unified dispatcher
# ---------------------------------------------------------------------------

def notify_cloud(url, classification, diff_preview, alert_to=None):
    """
    Dispatch notifications via every cloud provider that is configured.

    Providers are activated when their required env var is present:
      - AWS_SNS_TOPIC_ARN       → AWS SNS
      - AWS_SES_SENDER_EMAIL    → AWS SES
      - AZURE_COMMUNICATION_CONNECTION_STRING → Azure ACS Email

    Returns a dict with results keyed by provider name.
    """
    subject = f"[{classification.upper()}] Website Change Detected: {url}"
    body = (
        "Website Monitor Alert\n"
        "=====================\n"
        f"URL            : {url}\n"
        f"Classification : {classification.upper()}\n\n"
        "Changes Detected:\n"
        "-----------------\n"
        f"{diff_preview}\n\n"
        "--\n"
        "Sent by WatchDog Website Monitor (Cloud Alerts)\n"
    )

    results = {}

    # Resolve recipients for email-based providers
    recipients_str = alert_to or os.getenv("ALERT_TO", "")
    recipients = [e.strip() for e in recipients_str.split(",") if e.strip()]

    # AWS SNS -----------------------------------------------------------------
    if os.getenv("AWS_SNS_TOPIC_ARN"):
        ok, info = send_aws_sns(subject, body)
        results["aws_sns"] = {"ok": ok, "info": str(info)}
        print(f"  {'✅' if ok else '❌'} AWS SNS: {info}")

    # AWS SES -----------------------------------------------------------------
    if os.getenv("AWS_SES_SENDER_EMAIL") and recipients:
        ok, info = send_aws_ses(subject, body, recipients)
        results["aws_ses"] = {"ok": ok, "info": str(info)}
        print(f"  {'✅' if ok else '❌'} AWS SES → {', '.join(recipients)}: {info}")

    # Azure ACS Email ---------------------------------------------------------
    if os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING") and recipients:
        ok, info = send_azure_acs_email(subject, body, recipients)
        results["azure_acs"] = {"ok": ok, "info": str(info)}
        print(f"  {'✅' if ok else '❌'} Azure ACS Email → {', '.join(recipients)}: {info}")

    return results


def get_cloud_status():
    """
    Return the configuration status of each cloud integration.
    Used by the /api/cloud-status endpoint.
    """
    return {
        "aws_sns": {
            "configured": bool(os.getenv("AWS_SNS_TOPIC_ARN")),
            "label": "AWS SNS",
            "description": "1,000 notifications/month free",
            "docs": "https://docs.aws.amazon.com/sns/latest/dg/welcome.html",
        },
        "aws_ses": {
            "configured": bool(os.getenv("AWS_SES_SENDER_EMAIL")),
            "label": "AWS SES",
            "description": "200 emails/day free (sandbox)",
            "docs": "https://docs.aws.amazon.com/ses/latest/dg/Welcome.html",
        },
        "azure_acs": {
            "configured": bool(os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")),
            "label": "Azure ACS Email",
            "description": "100 emails/day free",
            "docs": "https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-overview",
        },
    }
