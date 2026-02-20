#!/usr/bin/env python3
"""TLDR AI collector — fetches AI news from tldr.tech via public RSS."""

import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

RSS_URL = "https://bullrich.dev/tldr-rss/ai.rss"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", ".data")
SEEN_FILE = os.path.join(DATA_DIR, "tldr_seen.jsonl")
KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30
MAX_NEW_ITEMS = 30  # cap output per run


def fetch_items():
    items = []
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "openclaw-tldr/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tree = ET.parse(resp)
    except Exception as e:
        print(f"# WARN: TLDR RSS fetch failed: {e}", file=sys.stderr)
        return items

    for item in tree.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        desc_el = item.find("description")

        title = (title_el.text or "").strip() if title_el is not None else ""
        guid_el = item.find("guid")
        link = (link_el.text or "").strip() if link_el is not None else ""
        if not link:
            link = (guid_el.text or "").strip() if guid_el is not None else ""
        desc = (desc_el.text or "").strip() if desc_el is not None else ""

        ts = 0
        if pub_el is not None and pub_el.text:
            try:
                dt = parsedate_to_datetime(pub_el.text)
                ts = dt.timestamp()
            except Exception:
                pass

        if not link or not title:
            continue
        # Skip sponsor posts
        if "(sponsor)" in title.lower():
            continue

        items.append({
            "title": title,
            "url": link,
            "source": "TLDR",
            "time": ts,
            "score": 0,
            "description": desc,
        })
    return items


def load_seen():
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
    cutoff = time.time() - MAX_AGE_DAYS * 86400
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for entry in seen.values():
            if entry.get("time", 0) > cutoff or entry.get("time", 0) == 0:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def format_output(items):
    if not items:
        return ""
    lines = []
    for i, item in enumerate(items, 1):
        ts = ""
        if item["time"]:
            dt = datetime.fromtimestamp(item["time"], KST)
            ts = dt.strftime("%y%m%d.%H:%M")
        line = f"{i}. [{item['title']}]({item['url']}) - [{ts}] [TLDR]"
        lines.append(line)
    return "\n".join(lines)


def main():
    seen = load_seen()
    new_items = []

    items = fetch_items()
    for item in items:
        if item["url"] not in seen:
            new_items.append(item)
            seen[item["url"]] = item

    save_seen(seen)

    # No time filter — seen file handles dedup, just cap output
    capped = new_items[:MAX_NEW_ITEMS]
    print(f"# Seen: {len(seen)} total, {len(new_items)} new, outputting {len(capped)}", file=sys.stderr)

    output = format_output(capped)
    if output:
        print(output)
    else:
        print("NO_NEW_TLDR", file=sys.stderr)


if __name__ == "__main__":
    main()
