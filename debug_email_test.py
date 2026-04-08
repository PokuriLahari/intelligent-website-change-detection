#!/usr/bin/env python3
"""
Debug script to test email routing end-to-end
"""
import json
from pathlib import Path

# Load a site with custom email
sites_file = Path("data/sites.json")
with open(sites_file) as f:
    sites = json.load(f)

# Find a site with different email
target_site = next((s for s in sites if s.get("alert_email") != "pokurilahari16@gmail.com"), None)

if target_site:
    print("=" * 70)
    print("TEST: Email routing for site with custom email")
    print("=" * 70)
    print(f"\nSite URL: {target_site['url']}")
    print(f"Site ID: {target_site['id']}")
    print(f"Configured Email: {target_site.get('alert_email')}")
    print(f"\nWhen you click ↻ for this site:")
    print(f"1. Dashboard calls: POST /api/check with data: {{'site_id': '{target_site['id']}'}}")
    print(f"2. Server should:")
    print(f"   - Find site by ID ✅")
    print(f"   - Get site_config with alert_email = {target_site.get('alert_email')}")
    print(f"   - Pass site_config to run_check() ✅")
    print(f"   - Pass site_config to send_alert() ✅")
    print(f"3. alerts.py should:")
    print(f"   - See site_config ✅")
    print(f"   - See alert_email field ✅")
    print(f"   - Use: {target_site.get('alert_email')} (NOT pokurilahari16@gmail.com)")
    print(f"\nConsole should show:")
    print(f"  📧 Using SITE EMAIL: {target_site.get('alert_email')}")
    print(f"  ✅ Email sent to {target_site.get('alert_email')}")
    print("\n" + "=" * 70)
    print("To test, run:")
    print("1. python app.py")
    print(f"2. Click ↻ for: {target_site['url']}")
    print("3. Check console output above")
    print("=" * 70)
else:
    print("❌ No sites with custom email found")
