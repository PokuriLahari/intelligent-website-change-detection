#!/usr/bin/env python3
"""
Test script to verify email routing is fixed.
This will trigger a test alert and show which email it goes to.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("  EMAIL ROUTING DIAGNOSTIC TEST")
print("=" * 80)

# Check .env configuration
print("\n1. CHECKING .env CONFIGURATION:")
print(f"   SMTP_USER: {os.getenv('SMTP_USER')}")
print(f"   SMTP_PASS: {'*' * 10} (hidden)")
print(f"   ALERT_FROM: {os.getenv('ALERT_FROM')}")
print(f"   DEFAULT ALERT_TO: {os.getenv('ALERT_TO')}")

# Load sites
sites_file = Path("data/sites.json")
if sites_file.exists():
    with open(sites_file) as f:
        sites = json.load(f)
    
    print(f"\n2. SITES WITH CUSTOM EMAILS ({len(sites)} total):")
    
    custom_email_sites = [s for s in sites if s.get("alert_email") and s.get("alert_email") != os.getenv("ALERT_TO")]
    
    if custom_email_sites:
        for i, site in enumerate(custom_email_sites[:3], 1):
            print(f"\n   Site #{i}:")
            print(f"   URL: {site['url']}")
            print(f"   Expected Email: {site['alert_email']}")
            print(f"   Site ID: {site['id'][:8]}...")
    else:
        print("   ❌ No sites with different emails found!")
        print("   Add a site with an email different from the default.")

print("\n" + "=" * 80)
print("  TEST INSTRUCTIONS:")
print("=" * 80)
print("""
1. Start the server:
   python app.py

2. In another terminal, run:
   python -c "
import requests
sites = {}
with open('data/sites.json') as f:
    import json
    sites_list = json.load(f)
    site_with_custom_email = next((s for s in sites_list if s.get('alert_email') and s.get('alert_email') != 'pokurilahari16@gmail.com'), None)
    if site_with_custom_email:
        print(f'Testing with: {site_with_custom_email[\"url\"]}')
        print(f'Expected email: {site_with_custom_email.get(\"alert_email\")}')
        response = requests.post('http://localhost:5000/api/check', json={'site_id': site_with_custom_email['id']})
        print(f'Response: {response.json()}')
"

3. WATCH THE CONSOLE for:
   ✅ "Using SITE EMAIL: [custom email]" 
   ✅ "Email sent to [custom email]"
   
   If you see:
   ❌ "Using DEFAULT EMAIL"
   ❌ "Email sent to pokurilahari16@gmail.com"
   
   Then the fix didn't work.

4. Check the email inbox for where the alert was actually sent.
""")
print("=" * 80)
