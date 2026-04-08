#!/usr/bin/env python3
"""
Test script to verify email routing logic works correctly.
This helps debug which email should be used for each site.
"""

import json
from pathlib import Path

# Load sites data
sites_file = Path("data/sites.json")
if not sites_file.exists():
    print("❌ data/sites.json not found")
    exit(1)

with open(sites_file) as f:
    sites = json.load(f)

print("=" * 70)
print("  EMAIL ROUTING TEST - Checking which email each site should use")
print("=" * 70)

for i, site in enumerate(sites):
    site_id = site.get("id", "UNKNOWN")
    url = site.get("url", "UNKNOWN")
    alert_email = site.get("alert_email")
    
    print(f"\n{i+1}. Site: {url}")
    print(f"   ID: {site_id[:8]}...")
    
    if alert_email:
        print(f"   ✅ Email: {alert_email} (SITE SPECIFIC)")
    else:
        print(f"   ⚠️  No alert_email - will use DEFAULT from .env")

print("\n" + "=" * 70)
print("  VERIFICATION:")
print("=" * 70)

# Check for duplicate alert emails
emails = {}
for site in sites:
    email = site.get("alert_email")
    if email:
        if email not in emails:
            emails[email] = []
        emails[email].append(site.get("url"))

print("\n📧 Email -> Sites mapping:")
for email, site_list in emails.items():
    print(f"\n{email}:")
    for url in site_list:
        print(f"  • {url}")

# Check if all sites have unique emails
print("\n" + "=" * 70)
if len(sites) == len(emails):
    print("✅ All sites have different email addresses")
else:
    print(f"⚠️  {len(sites)} sites but only {len(emails)} unique emails")
    print("   (Some sites share the same alert email)")

print("\nTo test email routing:")
print("1. Run: python app.py")
print("2. Click ↻ button for each site")
print("3. Check console for debug messages:")
print("   - 'Using SITE EMAIL' = Correct!")
print("   - 'Using DEFAULT EMAIL' = Problem!")
print("=" * 70)
