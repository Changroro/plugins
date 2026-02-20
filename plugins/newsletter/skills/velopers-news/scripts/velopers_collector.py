#!/usr/bin/env python3
"""Velopers collector — fetches items from velopers.kr RSS."""

import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", ".data")
SEEN_FILE = os.path.join(DATA_DIR, "velopers_seen.jsonl")
KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30
MAX_NEW_ITEMS = 30


def fetch_items():
    items = []
    req = urllib.request.Request(
        "https://www.velopers.kr/rss.xml",
        headers={"User-Agent": "openclaw-velopers/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            tree = ET.parse(resp)
    except Exception as e:
        print(f"# WARN: velopers.kr fetch failed: {e}", file=sys.stderr)
        return items

    for item in tree.findall(".//item"):
        title = (item.find("title").text or "").strip()
        link = (item.find("link").text or "").strip()
        pub = item.find("pubDate")
        pub_text = pub.text if pub is not None else ""
        ts = 0
        if pub_text:
            try:
                dt = parsedate_to_datetime(pub_text)
                ts = dt.timestamp()
            except Exception:
                pass
        if not link:
            continue
        items.append({
            "title": title,
            "url": link,
            "source": "Velopers",
            "time": ts,
            "score": 0,
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
        line = f"{i}. [{item['title']}]({item['url']}) - [{ts}] [Velopers]"
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

    capped = new_items[:MAX_NEW_ITEMS]
    print(f"# Seen: {len(seen)} total, {len(new_items)} new, outputting {len(capped)}", file=sys.stderr)

    output = format_output(capped)
    if output:
        print(output)
    else:
        print("NO_NEW_VELOPERS", file=sys.stderr)


if __name__ == "__main__":
    main()
