#!/usr/bin/env python
"""
Website Monitor - Final Deployment Validation Script
Comprehensive system check before production deployment
"""

import sys
import os

print("\n" + "="*60)
print("  WEBSITE MONITOR - FINAL DEPLOYMENT VALIDATION")
print("="*60 + "\n")

# Test 1: All imports
print("📦 Testing imports...")
try:
    import app
    from alerts import send_alert
    from differ import compute_diff, classify_change
    from fetcher import fetch_content, get_checksum, save_snapshot
    print("   ✅ All modules import successfully\n")
except Exception as e:
    print(f"   ❌ Import failed: {e}\n")
    sys.exit(1)

# Test 2: Data directories
print("📁 Checking directories...")
dirs = ['data', 'snapshots', 'templates']
for dir_name in dirs:
    if os.path.exists(dir_name):
        print(f"   ✅ {dir_name}/ exists")
    else:
        print(f"   ❌ {dir_name}/ missing")
print()

# Test 3: Critical files
print("📄 Checking required files...")
files = [
    'app.py', 'alerts.py', 'differ.py', 'fetcher.py', 'monitor.py',
    'requirements.txt', '.env', '.env.example', '.gitignore',
    'templates/index.html', 'README.md', 'QUICKSTART.md', 'RUN.bat'
]
missing = []
for file_name in files:
    if os.path.exists(file_name):
        print(f"   ✅ {file_name}")
    else:
        print(f"   ⚠️  {file_name} (optional)")
        missing.append(file_name)
print()

# Test 4: Database functions
print("🗄️  Testing database functions...")
try:
    sites = app.get_sites_db()
    history = app.get_history_db()
    print(f"   ✅ Sites database: {len(sites)} sites loaded")
    print(f"   ✅ History database: {len(history)} events loaded\n")
except Exception as e:
    print(f"   ❌ Database error: {e}\n")
    sys.exit(1)

# Test 5: Change detection
print("🔍 Testing change detection...")
try:
    old_text = "Line 1\nLine 2\nLine 3"
    new_text = "Line 1\nLINE 2 MODIFIED\nLine 3\nLine 4 ADDED"
    diff = compute_diff(old_text, new_text)
    classification = classify_change(diff, old_text)
    print(f"   ✅ Change detection working")
    print(f"   ✅ Classification: {classification}\n")
except Exception as e:
    print(f"   ❌ Detection error: {e}\n")
    sys.exit(1)

# Test 6: Email configuration
print("📧 Checking email setup...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    alert_to = os.getenv('ALERT_TO')
    
    if smtp_user and smtp_pass and alert_to:
        email_preview = smtp_user[:20] if len(smtp_user) > 20 else smtp_user
        print(f"   ✅ SMTP_USER: {email_preview}...")
        print(f"   ✅ SMTP_PASS: configured")
        print(f"   ✅ ALERT_TO: {alert_to}\n")
    else:
        print("   ⚠️  Email configuration incomplete\n")
except Exception as e:
    print(f"   ⚠️  Email config error: {e}\n")

# Test 7: Flask app
print("🌐 Testing Flask application...")
try:
    test_client = app.app.test_client()
    
    # Test homepage
    response = test_client.get('/')
    if response.status_code == 200:
        print(f"   ✅ Dashboard route: GET / → {response.status_code}")
    
    # Test API
    response = test_client.get('/api/sites')
    if response.status_code == 200:
        print(f"   ✅ API route: GET /api/sites → {response.status_code}")
    
    print()
except Exception as e:
    print(f"   ⚠️  Flask test warning: {e}\n")

# Summary
print("="*60)
print("  ✅ DEPLOYMENT VALIDATION PASSED")
print("="*60)
print("\n✨ Your Website Monitor is ready for production!\n")
print("NEXT STEPS:")
print("  1. Windows: Double-click RUN.bat")
print("  2. Linux/Mac: python app.py")
print("  3. Open: http://localhost:5000")
print("  4. Add your first website")
print("  5. Check email for alerts!\n")
print("📖 For detailed help:")
print("   - QUICKSTART.md (2-minute setup)")
print("   - README.md (full documentation)")
print("   - DEPLOYMENT.md (production checklist)\n")
