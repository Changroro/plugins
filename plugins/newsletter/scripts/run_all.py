#!/usr/bin/env python3
"""Unified newsletter runner — runs selected platform collectors in parallel."""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_collector import format_output

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", ".data", "config.json")

COLLECTOR_MAP = {
    "hn": "collectors.hn",
    "reddit": "collectors.reddit",
    "geeknews": "collectors.geeknews",
    "tldr": "collectors.tldr",
    "threads": "collectors.threads",
    "velopers": "collectors.velopers",
    "devday": "collectors.devday",
}

DEFAULT_PLATFORMS = ["hn", "reddit", "geeknews", "tldr", "threads", "velopers", "devday"]


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"platforms": DEFAULT_PLATFORMS}


def run_collector(platform, config):
    import importlib
    module_name = COLLECTOR_MAP.get(platform)
    if not module_name:
        print(f"# WARN: unknown platform {platform}", file=sys.stderr)
        return []

    mod = importlib.import_module(module_name)

    kwargs = {}
    if platform == "reddit" and "subreddits" in config:
        kwargs["subreddits"] = config["subreddits"]
    elif platform == "threads" and "threads_accounts" in config:
        kwargs["accounts"] = config["threads_accounts"]

    return mod.collect(**kwargs)


def main():
    config = load_config()
    platforms = config.get("platforms", DEFAULT_PLATFORMS)
    all_items = []
    seen_urls = set()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(run_collector, p, config): p
            for p in platforms
        }
        for future in as_completed(futures):
            platform = futures[future]
            try:
                items = future.result()
                for item in items:
                    if item["url"] not in seen_urls:
                        seen_urls.add(item["url"])
                        all_items.append(item)
                print(f"# {platform}: {len(items)} items", file=sys.stderr)
            except Exception as e:
                print(f"# ERROR: {platform} failed: {e}", file=sys.stderr)

    all_items.sort(key=lambda x: x.get("time", 0), reverse=True)

    output = format_output(all_items)
    if output:
        print(output)
    else:
        print("NO_NEW_ITEMS", file=sys.stderr)

    return all_items


if __name__ == "__main__":
    main()
