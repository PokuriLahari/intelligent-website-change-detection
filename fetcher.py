import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
import time
import random
from datetime import datetime

SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def fetch_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/123.0.0.0 Safari/537.36",
        "Accept":            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language":   "en-US,en;q=0.9",
        "Accept-Encoding":   "gzip, deflate, br",
        "Referer":           "https://www.google.com/",
        "DNT":               "1",
        "Connection":        "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    time.sleep(random.uniform(2, 5))

    session = requests.Session()
    session.headers.update(headers)

    response = session.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript", "meta", "head"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)


def get_checksum(content):
    return hashlib.sha256(content.encode()).hexdigest()


def save_snapshot(url, content, checksum=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "").strip("_")
    filename = os.path.join(SNAPSHOT_DIR, f"{safe_url}_{timestamp}.json")

    data = {
        "url": url,
        "timestamp": timestamp,
        "checksum": checksum or get_checksum(content),
        "content": content
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filename