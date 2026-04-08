from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import glob
import threading
import time
import hashlib
import uuid
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import difflib
import urllib3
from alerts import send_alert

app = Flask(__name__)
CORS(app)
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500

# Thread safety lock for file operations
file_lock = threading.Lock()

DATA_DIR = "data"
SITES_FILE = os.path.join(DATA_DIR, "sites.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
SNAPSHOT_DIR = "snapshots"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def load_json_file(path, default):
    with file_lock:
        if not os.path.exists(path):
            return default
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default


def save_json_file(path, data):
    # Ensure directory exists before writing
    with file_lock:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def safe_key(url):
    return (
        url.replace("https://", "")
           .replace("http://", "")
           .replace("www.", "")
           .replace("/", "_")
           .replace(":", "")
           .strip("_")
    )

# ===================== HELPERS =====================

def fetch_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=20, verify=False)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "iframe", "header"]):
        tag.decompose()

    main = soup.find("main") or soup.find("article") or soup.body
    return main.get_text(separator="\n", strip=True)

def get_checksum(content):
    return hashlib.sha256(content.encode()).hexdigest()

def compute_diff(old, new):
    return list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=""))

def classify_change(diff, old_content):
    added   = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]

    total = len(added) + len(removed)
    ratio = total / (len(old_content.splitlines()) or 1)

    if ratio > 0.10 or total > 20:
        return "major"
    elif total > 3:
        return "minor"
    else:
        return "none"


# ===================== STORAGE =====================

def get_last_snapshot(url):
    safe_url = safe_key(url)
    
    # Check for both .json (new format) and .txt (legacy format)
    json_pattern = os.path.join(SNAPSHOT_DIR, f"{safe_url}_*.json")
    txt_pattern = os.path.join(SNAPSHOT_DIR, f"{safe_url}_*.txt")
    
    files = sorted(glob.glob(json_pattern) + glob.glob(txt_pattern))
    
    if not files:
        return None
    
    latest = files[-1]
    
    # Handle .json files
    if latest.endswith(".json"):
        with open(latest, encoding="utf-8") as f:
            return json.load(f)
    
    # Handle legacy .txt files
    elif latest.endswith(".txt"):
        with open(latest, encoding="utf-8") as f:
            content = f.read()
            return {
                "content": content,
                "checksum": get_checksum(content),
                "url": url
            }
    
    return None


def save_snapshot(url, content, checksum):
    safe_url = safe_key(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SNAPSHOT_DIR, f"{safe_url}_{timestamp}.json")

    data = {
        "url": url,
        "timestamp": timestamp,
        "checksum": checksum,
        "content": content
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filename

# ===================== DATABASE =====================

def add_site_db(url, interval, **kwargs):
    sites = get_sites_db()
    item = {
        "id": str(uuid.uuid4()),
        "url": url,
        "interval_minutes": interval,
        "last_checked": None,
        "last_run_ts": 0,
        "created_at": datetime.now().isoformat()
    }
    # Add optional fields if provided
    if "alert_email" in kwargs and kwargs["alert_email"]:
        item["alert_email"] = kwargs["alert_email"]
    if "keywords" in kwargs and kwargs["keywords"]:
        item["keywords"] = kwargs["keywords"]
    sites.append(item)
    save_sites_db(sites)
    return item

def get_sites_db():
    return load_json_file(SITES_FILE, [])


def save_sites_db(sites):
    save_json_file(SITES_FILE, sites)


def delete_site_db(site_id):
    sites = [site for site in get_sites_db() if site["id"] != site_id]
    save_sites_db(sites)

def save_history_db(url, classification):
    history = get_history_db()
    item = {
        "id": str(uuid.uuid4()),
        "url": url,
        "classification": classification,
        "timestamp": datetime.now().isoformat()
    }
    history.append(item)
    save_json_file(HISTORY_FILE, history)

def get_history_db():
    return load_json_file(HISTORY_FILE, [])

# ===================== CORE =====================

def run_check(url, site_config=None):
    try:
        content  = fetch_content(url)
        checksum = get_checksum(content)

        last = get_last_snapshot(url)

        if last:
            if last["checksum"] == checksum:
                print("✅ No change detected")
                return {"status": "no_change"}

            diff = compute_diff(last["content"], content)
            classification = classify_change(diff, last["content"])

            print(f"🚨 Change detected: {classification.upper()}")

            save_history_db(url, classification)
            if classification in ("major", "minor"):
                # Pass site configuration to send_alert for per-site email settings
                send_alert(url, classification, diff, site_config=site_config)

        else:
            print("🆕 First snapshot")

        save_snapshot(url, content, checksum)

        return {"status": "ok"}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"status": "error", "error": str(e)}

# ===================== BACKGROUND =====================

def background_worker():
    print("🔄 Background monitor started")
    while True:
        try:
            sites = get_sites_db()
            now = time.time()

            for site in sites:
                try:
                    interval = site.get("interval_minutes", 60) * 60
                    last_run = site.get("last_run_ts", 0)

                    if now - last_run >= interval:
                        # Pass site configuration for per-site email settings
                        result = run_check(site["url"], site_config=site)

                        site["last_run_ts"] = now
                        site["last_checked"] = datetime.now().isoformat()
                        site["last_status"] = result.get("status")

                        saved_sites = get_sites_db()
                        for saved_site in saved_sites:
                            if saved_site["id"] == site["id"]:
                                saved_site.update(site)
                                break
                        save_sites_db(saved_sites)
                except Exception as e:
                    print(f"[ERROR] Failed to check {site.get('url')}: {e}")
                    continue

            time.sleep(30)
        except Exception as e:
            print(f"[ERROR] Background worker error: {e}")
            time.sleep(30)

# ===================== CORS & HEADERS =====================

@app.after_request
def inject_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ===================== ROUTES =====================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/sites", methods=["GET"])
def get_sites():
    try:
        return jsonify(get_sites_db()), 200
    except Exception as e:
        print(f"[ERROR] get_sites: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/sites", methods=["POST"])
def add_site():
    try:
        if not request.json:
            return jsonify({"error": "Request body required"}), 400
        
        data = request.json
        url = data.get("url", "").strip()
        
        # Validate URL
        if not url:
            return jsonify({"error": "URL required"}), 400
        
        try:
            interval = int(data.get("interval_minutes", 60))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid interval"}), 400
        
        # Extract optional fields
        alert_email = data.get("alert_email", "").strip() or None
        keywords = data.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",") if k.strip()]
        
        site = add_site_db(url, interval, alert_email=alert_email, keywords=keywords)
        return jsonify(site), 201
    except Exception as e:
        print(f"[ERROR] add_site: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/sites/<site_id>", methods=["DELETE"])
def delete_site(site_id):
    try:
        delete_site_db(site_id)
        return jsonify({"ok": True}), 200
    except Exception as e:
        print(f"[ERROR] delete_site: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/check", methods=["POST"])
def manual_check():
    try:
        if not request.json and request.data:
            return jsonify({"error": "Invalid request body"}), 400
        
        data = request.json or {}
        site_id = data.get("site_id")
        url = data.get("url")
        
        # Case 1: Check specific site by ID
        if site_id:
            sites = get_sites_db()
            site = next((s for s in sites if s["id"] == site_id), None)
            if not site:
                return jsonify({"status": "error", "error": "site not found"}), 404
            url = site["url"]
            # Pass site configuration for per-site email settings
            result = run_check(url, site_config=site)
            return jsonify(result), 200
        
        # Case 2: Check specific site by URL
        if url:
            # Try to find the site config in database
            sites = get_sites_db()
            site_config = next((s for s in sites if s["url"] == url), None)
            result = run_check(url, site_config=site_config)
            return jsonify(result), 200
        
        # Case 3: Empty body - check all sites
        sites = get_sites_db()
        if not sites:
            return jsonify({"status": "ok", "checked": 0}), 200
        
        results = []
        for site in sites:
            # Pass site configuration for per-site email settings
            result = run_check(site["url"], site_config=site)
            results.append({"url": site["url"], "status": result.get("status")})
        
        return jsonify({"status": "ok", "checked": len(sites), "results": results}), 200
    except Exception as e:
        print(f"[ERROR] manual_check: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        return jsonify(get_history_db()), 200
    except Exception as e:
        print(f"[ERROR] get_history: {e}")
        return jsonify({"error": str(e)}), 500

# ===================== RUN =====================

if __name__ == "__main__":
    # Start background worker thread
    threading.Thread(target=background_worker, daemon=True).start()
    
    # Check environment variable
    is_production = os.getenv("FLASK_ENV") == "production" or os.getenv("PRODUCTION") == "true"
    
    if is_production:
        print("🚀 Server running in PRODUCTION mode on http://0.0.0.0:5000")
        try:
            from waitress import serve
            serve(app, host="0.0.0.0", port=5000, threads=4)
        except ImportError:
            print("ERROR: waitress not installed. Run: pip install waitress")
            print("Falling back to Flask dev server...")
            app.run(host="0.0.0.0", debug=False, port=5000)
    else:
        print("🚀 Server running in DEVELOPMENT mode at http://0.0.0.0:5000")
        app.run(host="0.0.0.0", debug=True, port=5000, use_reloader=False)