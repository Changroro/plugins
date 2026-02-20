#!/usr/bin/env python3
"""Reddit AI collector — fetches AI-related posts from key subreddits."""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", ".data")
SEEN_FILE = os.path.join(DATA_DIR, "reddit_seen.jsonl")
KST = timezone(timedelta(hours=9))
MAX_AGE_DAYS = 30
OUTPUT_MAX_AGE_HOURS = 1
SUBREDDITS = [
    "Anthropic", "ArtificialInteligence", "ClaudeAI", "GithubCopilot",
    "LocalLLaMA", "ollama", "OpenAI", "openclaw", "opensource", "Qwen_AI", "Vllm",
]

AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "anthropic", "openai", "gemini", "mistral",
    "llama", "qwen", "deepseek", "copilot", "chatgpt", "transformer", "diffusion",
    "stable diffusion", "midjourney", "dall-e", "sora", "neural", "machine learning",
    "deep learning", "langchain", "llamaindex", "hugging face", "huggingface",
    "nvidia", "cuda", "gpu", "rag", "vector", "embedding", "fine-tune", "finetune",
    "lora", "qlora", "quantiz", "gguf", "ggml", "ollama", "vllm", "mlx",
    "agent", "mcp", "tool use", "function calling", "reasoning", "chain of thought",
    "benchmark", "eval", "arxiv", "paper", "model", "inference", "training",
    "open source", "opensource", "open-source", "foundation model", "multimodal",
    "vision", "speech", "tts", "stt", "whisper", "grok", "xai", "cohere",
    "meta ai", "gemma", "phi", "openclaw", "cursor", "windsurf", "aider",
    "coding agent", "code generation", "robotics", "autonomous", "self-driving",
]


def is_ai_related(title, url=""):
    text = (title + " " + url).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def fetch_json(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-reddit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"# WARN: fetch failed {url}: {e}", file=sys.stderr)
        return None


def fetch_items():
    seen_urls = set()
    items = []
    cutoff = time.time() - 1 * 3600
    endpoints = ["hot.json?limit=30", "rising.json?limit=20"]
    for sub in SUBREDDITS:
        for endpoint in endpoints:
            data = fetch_json(f"https://www.reddit.com/r/{sub}/{endpoint}")
            if not data or "data" not in data:
                continue
            for post in data["data"]["children"]:
                d = post["data"]
                created = d.get("created_utc", 0)
                if created < cutoff:
                    continue
                title = d.get("title", "")
                url = d.get("url", "")
                permalink = f"https://reddit.com{d.get('permalink', '')}"
                if permalink in seen_urls:
                    continue
                seen_urls.add(permalink)
                score = d.get("score", 0)
                if not is_ai_related(title, url):
                    continue
                items.append({
                    "title": title,
                    "url": permalink,
                    "source": f"r/{sub}",
                    "time": created,
                    "score": score,
                })
    items.sort(key=lambda x: x.get("score", 0), reverse=True)
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
        line = f"{i}. [{item['title']}]({item['url']}) - [{ts}] [{item['source']}|{item['score']}pt]"
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

    output_cutoff = time.time() - OUTPUT_MAX_AGE_HOURS * 3600
    recent = [i for i in new_items if i.get("time", 0) > output_cutoff]
    print(f"# Seen: {len(seen)} total, {len(new_items)} new, {len(recent)} recent", file=sys.stderr)

    output = format_output(recent)
    if output:
        print(output)
    else:
        print("NO_NEW_REDDIT", file=sys.stderr)


if __name__ == "__main__":
    main()
