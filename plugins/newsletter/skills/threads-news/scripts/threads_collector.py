#!/usr/bin/env python3
"""Threads post collector — polls RSSHub and outputs only new posts."""

import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

RSSHUB_BASE = os.environ.get("RSSHUB_URL", "http://rsshub-rsshub-1:1200")
ACCOUNTS = ["choi.openai", "claudeai", "programmingzombie", "feelfree_ai"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", ".data")
SEEN_FILE = os.path.join(DATA_DIR, "threads_seen.jsonl")
KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30
OUTPUT_MAX_AGE_HOURS = 24


def fetch_threads(account):
    """Fetch posts from a Threads account via RSSHub."""
    url = f"{RSSHUB_BASE}/threads/{account}"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-threads/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tree = ET.parse(resp)
    except Exception as e:
        print(f"# WARN: fetch failed @{account}: {e}", file=sys.stderr)
        return []

    items = []
    for item in tree.findall(".//item"):
        title = (item.find("title").text or "").strip()
        link = (item.find("link").text or "").strip()
        desc_el = item.find("description")
        desc = (desc_el.text or "").strip() if desc_el is not None else ""
        pub = item.find("pubDate")
        ts = 0
        if pub is not None and pub.text:
            try:
                dt = parsedate_to_datetime(pub.text)
                ts = dt.timestamp()
            except Exception:
                pass
        if not link:
            continue
        items.append({
            "title": title,
            "url": link,
            "source": f"Threads/@{account}",
            "time": ts,
            "score": 0,
            "description": desc,
        })
    return items


def load_seen():
    """Load seen URLs from file."""
    seen = {}
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    seen[entry["url"]] = entry
    except FileNotFoundError:
        pass
    return seen


def save_seen(seen):
    """Save seen entries, pruning old ones."""
    cutoff = time.time() - MAX_AGE_DAYS * 86400
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for entry in seen.values():
            if entry.get("time", 0) > cutoff or entry.get("time", 0) == 0:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def format_output(new_items):
    """Format new items for stdout."""
    if not new_items:
        return ""
    lines = []
    for i, item in enumerate(new_items, 1):
        ts = ""
        if item["time"]:
            dt = datetime.fromtimestamp(item["time"], KST)
            ts = dt.strftime("%y%m%d.%H:%M")
        line = f"{i}. [{item['title']}]({item['url']}) - [{ts}] [{item['source']}]"
        lines.append(line)
    return "\n".join(lines)


def main():
    seen = load_seen()
    new_items = []

    for account in ACCOUNTS:
        items = fetch_threads(account)
        for item in items:
            if item["url"] not in seen:
                new_items.append(item)
                seen[item["url"]] = item
                print(f"# NEW: @{account} — {item['title'][:60]}", file=sys.stderr)

    save_seen(seen)

    # Only output items from the last 24 hours
    output_cutoff = time.time() - OUTPUT_MAX_AGE_HOURS * 3600
    recent_items = [item for item in new_items if item.get("time", 0) > output_cutoff]
    print(f"# Seen: {len(seen)} total, {len(new_items)} new, {len(recent_items)} recent", file=sys.stderr)

    output = format_output(recent_items)
    if output:
        print(output)
    else:
        print("NO_NEW_THREADS", file=sys.stderr)


if __name__ == "__main__":
    main()
