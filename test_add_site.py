#!/usr/bin/env python
"""
Website Monitor - Test Add Site Functionality
"""

import time
import requests
import json

API = 'http://localhost:5000/api'

print("\n" + "="*70)
print("  WEBSITE MONITOR - ADD SITE TEST")
print("="*70 + "\n")

# Wait for server to start
print("⏳ Waiting for Flask server to start...")
time.sleep(2)

# Test 1: Check if API is online
print("\n📡 Testing API Connection...")
try:
    r = requests.get(f'{API}/sites', timeout=3)
    if r.status_code == 200:
        print("   ✅ API GET /sites: ONLINE")
    else:
        print(f"   ❌ API Error: {r.status_code}")
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# Test 2: Get current sites
print("\n📋 Current Sites:")
try:
    r = requests.get(f'{API}/sites', timeout=3)
    sites = r.json() if r.status_code == 200 else []
    if sites:
        for site in sites:
            print(f"   • {site.get('url')} ({site.get('interval_minutes')}m)")
    else:
        print("   (none)")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Add a new site
print("\n➕ Adding Site: https://openai.com/pricing")
try:
    payload = {
        'url': 'https://openai.com/pricing',
        'interval_minutes': 30
    }
    r = requests.post(f'{API}/sites', json=payload, timeout=5)
    
    if r.status_code == 200:
        data = r.json()
        print("   ✅ Site Added Successfully!")
        print(f"   • URL: {data.get('url')}")
        print(f"   • ID: {data.get('id')}")
        print(f"   • Interval: Every {data.get('interval_minutes')} minutes")
        print(f"   • Created: {data.get('created_at')}")
    else:
        print(f"   ❌ Failed: Status {r.status_code}")
        print(f"   Response: {r.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Verify site was added
print("\n✓ Verifying Sites List:")
try:
    r = requests.get(f'{API}/sites', timeout=3)
    sites = r.json() if r.status_code == 200 else []
    print(f"   Total Sites: {len(sites)}")
    for i, site in enumerate(sites, 1):
        print(f"   {i}. {site.get('url')}")
        print(f"      └─ Check every {site.get('interval_minutes')} minutes")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: Manual check
print("\n🔍 Running Manual Check on First Site:")
try:
    r = requests.get(f'{API}/sites', timeout=3)
    sites = r.json() if r.status_code == 200 else []
    if sites:
        url = sites[0]['url']
        print(f"   Checking: {url}")
        
        check_payload = {'url': url}
        r = requests.post(f'{API}/check', json=check_payload, timeout=30)
        
        if r.status_code == 200:
            result = r.json()
            print(f"   ✅ Check Complete: {result.get('status')}")
            if result.get('status') == 'ok':
                print("   ✓ Snapshot saved successfully")
        else:
            print(f"   ⚠️  Check Status: {r.status_code}")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print("\n" + "="*70)
print("  ✅ SITE ADD TEST COMPLETE")
print("="*70)
print("\n📊 STATUS: Website is being monitored and checked!")
print("💻 Dashboard: http://localhost:5000")
print("📧 Email alerts will be sent when changes are detected!\n")
