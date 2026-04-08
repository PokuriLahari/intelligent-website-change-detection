import requests
import schedule
import time
import json
import os
import glob
from fetcher import fetch_content, get_checksum, save_snapshot
from differ  import compute_diff, classify_change
from alerts  import send_alert

SITES = [
    {"url": "https://quotes.toscrape.com",  "interval_minutes": 2},
    {"url": "https://books.toscrape.com",   "interval_minutes": 2},
    {"url": "https://news.ycombinator.com", "interval_minutes": 5},
]


def check_site(url):
    print(f"[{url}] Checking...")

    try:
        new_content = fetch_content(url)
    except requests.exceptions.ConnectionError:
        print(f"[{url}] ERROR: Could not connect. Check the URL.")
        return
    except requests.exceptions.Timeout:
        print(f"[{url}] ERROR: Request timed out.")
        return
    except requests.exceptions.HTTPError as e:
        print(f"[{url}] ERROR: HTTP {e.response.status_code}")
        return
    except Exception as e:
        print(f"[{url}] ERROR: {e}")
        return

    new_checksum = get_checksum(new_content)
    safe_url     = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "").strip("_")
    snapshots    = sorted(glob.glob(f"snapshots/{safe_url}_*.*"))

    if snapshots:
        with open(snapshots[-1], encoding="utf-8") as f:
            if snapshots[-1].endswith(".json"):
                last = json.load(f)
            else:
                last = {"content": f.read()}

        if last.get("checksum") == new_checksum:
            print(f"[{url}] No change detected.")
            return

        diff           = compute_diff(last["content"], new_content)
        classification = classify_change(diff, last["content"])
        print(f"[{url}] Change detected: {classification.upper()}")

        if classification in ("major", "minor"):
            send_alert(url, classification, diff)
    else:
        print(f"[{url}] First snapshot saved.")

    save_snapshot(url, new_content, new_checksum)
    print(f"[{url}] Done.")


# Schedule all sites
for site in SITES:
    schedule.every(site["interval_minutes"]).minutes.do(check_site, url=site["url"])

# Run immediately on startup, then follow the schedule
for site in SITES:
    check_site(site["url"])

while True:
    schedule.run_pending()
    time.sleep(30)