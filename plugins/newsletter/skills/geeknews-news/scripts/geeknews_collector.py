#!/usr/bin/env python3
"""GeekNews collector — scrapes news.hada.io for new items."""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", ".data")
SEEN_FILE = os.path.join(DATA_DIR, "geeknews_seen.jsonl")
KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30


def fetch_items():
    items = []
    for page_url in ["https://news.hada.io/new", "https://news.hada.io/"]:
        req = urllib.request.Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"# WARN: GeekNews fetch failed {page_url}: {e}", file=sys.stderr)
            continue

        pattern = r"<a\s+href='([^']+)'[^>]*><h1>([^<]+)</h1></a>\s*<span class=topicurl>\(([^)]+)\)</span></div><div class='topicdesc'><a href='topic\?id=(\w+)'"
        matches = re.findall(pattern, html)
        scores = {tid: int(s) for tid, s in re.findall(r"id='tp(\w+)'>(\d+)</span>", html)}

        for ext_url, title, domain, tid in matches:
            score = scores.get(tid, 0)
            items.append({
                "title": title.strip(),
                "url": ext_url,
                "source": "GeekNews",
                "time": 0,
                "score": score,
            })

    # dedupe by title
    seen_titles = set()
    deduped = []
    for it in items:
        if it["title"] not in seen_titles:
            seen_titles.add(it["title"])
            deduped.append(it)
    deduped.sort(key=lambda x: x.get("score", 0), reverse=True)
    return deduped


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
            # time=0 items: keep all (no timestamp to prune by)
            if entry.get("time", 0) > cutoff or entry.get("time", 0) == 0:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def format_output(items):
    if not items:
        return ""
    lines = []
    for i, item in enumerate(items, 1):
        line = f"{i}. [{item['title']}]({item['url']}) - [GeekNews|{item['score']}pt]"
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
        print("NO_NEW_GEEKNEWS", file=sys.stderr)


if __name__ == "__main__":
    main()
