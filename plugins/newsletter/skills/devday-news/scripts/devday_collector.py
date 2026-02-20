#!/usr/bin/env python3
"""DevDay collector — scrapes devday.kr/space/ai-data for AI articles."""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", ".data")
SEEN_FILE = os.path.join(DATA_DIR, "devday_seen.jsonl")
KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30


def fetch_items():
    items = []
    req = urllib.request.Request(
        "https://devday.kr/space/ai-data",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"# WARN: devday.kr fetch failed: {e}", file=sys.stderr)
        return items

    articles = re.findall(
        r'href=["\'](/article/[^"\']+)["\']',
        html,
    )
    blocks = re.findall(
        r'href=["\'](/article/([^"\']+))["\'].*?<[^>]*class=["\'][^"\']*title[^"\']*["\'][^>]*>([^<]+)<',
        html,
        re.DOTALL,
    )
    if blocks:
        seen_slugs = set()
        for path, slug, title in blocks:
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            items.append({
                "title": title.strip(),
                "url": f"https://devday.kr{path}",
                "source": "DevDay",
                "time": 0,
                "score": 0,
            })
    else:
        seen_slugs = set()
        for path in articles:
            slug = path.split("/article/")[-1]
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            title = slug.replace("-", " ").title()
            items.append({
                "title": title,
                "url": f"https://devday.kr{path}",
                "source": "DevDay",
                "time": 0,
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
        line = f"{i}. [{item['title']}]({item['url']}) - [DevDay]"
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
            print(f"# NEW: {item['title'][:60]}", file=sys.stderr)

    save_seen(seen)
    print(f"# Seen: {len(seen)} total, {len(new_items)} new", file=sys.stderr)

    output = format_output(new_items)
    if output:
        print(output)
    else:
        print("NO_NEW_DEVDAY", file=sys.stderr)


if __name__ == "__main__":
    main()
