#!/usr/bin/env python3
"""직행 API JSON을 파싱하여 옵시디언 마크다운 파일을 생성.

Usage:
    cat api_response.json | python3 parse_jobs.py --output-dir /path/to/공고/
    cat api_response.json | python3 parse_jobs.py --check-duplicates /path/to/공고/
"""

import json
import sys
import re
import os
import argparse
from datetime import datetime, timezone, timedelta


def parse_tiptap_to_markdown(doc: dict) -> dict:
    """TipTap JSON (summary)을 섹션별 마크다운으로 변환.

    Returns: {"담당업무": "- item1\\n- item2", "자격요건": "...", ...}
    """
    if not doc or doc.get("type") != "doc":
        return {}

    sections = {}
    current_section = None

    for node in doc.get("content", []):
        if node["type"] == "image":
            src = node.get("attrs", {}).get("src", "")
            if src:
                if "image" not in sections:
                    sections["image"] = f"![공고 이미지]({src})"
                else:
                    sections["image"] += f"\n![공고 이미지]({src})"
        elif node["type"] == "heading":
            texts = extract_texts(node)
            current_section = texts.strip()
        elif node["type"] == "bulletList" and current_section:
            items = []
            for li in node.get("content", []):
                text = extract_texts(li).strip()
                if text:
                    items.append(f"- {text}")
            if current_section in sections:
                sections[current_section] += "\n" + "\n".join(items)
            else:
                sections[current_section] = "\n".join(items)
        elif node["type"] == "paragraph" and current_section:
            text = extract_texts(node).strip()
            if text:
                if current_section in sections:
                    sections[current_section] += f"\n- {text}"
                else:
                    sections[current_section] = f"- {text}"

    return sections


def extract_texts(node: dict) -> str:
    """노드에서 텍스트를 재귀적으로 추출."""
    if node.get("type") == "text":
        return node.get("text", "")
    texts = []
    for child in node.get("content", []):
        texts.append(extract_texts(child))
    return " ".join(texts)


def format_career(career_min: int, career_max: int) -> str:
    """경력 조건을 사람이 읽을 수 있는 형태로 변환."""
    if career_min == 0 and career_max == 0:
        return "신입"
    if career_min == 0 and career_max >= 100:
        return "경력무관"
    if career_min > 0 and career_max >= 100:
        return f"{career_min}년 이상"
    if career_min == 0 and career_max < 100:
        return f"{career_max}년 이하"
    return f"{career_min}년~{career_max}년"


def format_deadline(deadline_type: str, end_date: str) -> str:
    """마감일을 포맷."""
    if deadline_type == "상시채용":
        return "상시"
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            now = datetime.now(timezone(timedelta(hours=9)))
            diff = (end.date() - now.date()).days
            if diff < 0:
                return "마감"
            return f"D-{diff}"
        except (ValueError, TypeError):
            return "상시"
    return "상시"


def sanitize_filename(name: str, max_len: int = 50) -> str:
    """파일명 안전하게 변환."""
    cleaned = re.sub(r'[/\\:*?"<>|]', '', name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned


def build_markdown(job: dict, detail_sections: dict) -> str:
    """공고 데이터로 옵시디언 마크다운 생성."""
    company = job.get("company", {}).get("name", "")
    title = job.get("title", "")
    career = format_career(job.get("careerMin", 0), job.get("careerMax", 0))
    emp_types = ", ".join(job.get("employeeTypes", []))
    regions = ", ".join(job.get("regions", []))
    deadline = format_deadline(job.get("deadlineType", ""), job.get("endDate"))
    source = job.get("affiliate", "")
    keywords = " ".join(f"#{k}" for k in job.get("keywords", []))
    url = f"https://zighang.com/recruitment/{job['id']}"

    lines = [
        "---",
        f"회사: {company}",
        f"지역: {regions}",
        f"고용형태: {emp_types}",
        f'경력조건: "{career}"',
        f"마감: {deadline}",
        f'link: "{url}"',
        "tags:",
        f'  - "{career}"',
        "---",
        "",
        f"# {company} - {title}",
    ]

    # 상세 섹션 추가
    section_order = ["image", "담당업무", "주요업무", "자격요건", "우대사항", "기술스택", "전형절차", "혜택 및 복지", "근무조건", "참고사항"]
    for section in section_order:
        if section in detail_sections and detail_sections[section].strip():
            if section == "image":
                lines.append(f"\n{detail_sections[section]}")
            else:
                lines.append(f"\n## {section}\n")
                lines.append(detail_sections[section])

    return "\n".join(lines) + "\n"


def get_existing_uuids(directory: str) -> set:
    """기존 문서에서 UUID 집합 추출."""
    uuids = set()
    if not os.path.isdir(directory):
        return uuids

    for fname in os.listdir(directory):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(directory, fname)
        in_frontmatter = False
        with open(fpath, "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped == "---" and not in_frontmatter:
                    in_frontmatter = True
                    continue
                if stripped == "---" and in_frontmatter:
                    break
                if in_frontmatter and line.startswith("link:"):
                    match = re.search(r"/recruitment/([a-f0-9-]{36})", line)
                    if match:
                        uuids.add(match.group(1))
                    break
    return uuids


def main():
    parser = argparse.ArgumentParser(description="직행 API JSON → 옵시디언 마크다운")
    parser.add_argument("--output-dir", default="/home/bch/obsidian_sync/개인/new_life/관심공고/")
    parser.add_argument("--check-duplicates", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.load(sys.stdin)

    # data는 [{list_data, detail_data}, ...] 형태
    if isinstance(data, dict) and "content" in data:
        jobs = data["content"]
    elif isinstance(data, list):
        jobs = data
    else:
        print(json.dumps({"error": "unexpected data format"}))
        sys.exit(1)

    existing_uuids = get_existing_uuids(args.output_dir) if args.check_duplicates else set()

    results = {"created": [], "skipped": [], "total": len(jobs)}

    os.makedirs(args.output_dir, exist_ok=True)

    for job in jobs:
        job_id = job.get("id", "")
        company = job.get("company", {}).get("name", "unknown")
        title = job.get("title", "unknown")

        if job_id in existing_uuids:
            results["skipped"].append(f"{company} - {title}")
            continue

        # Parse detail summary
        detail_sections = {}
        if "summary" in job and job["summary"]:
            detail_sections = parse_tiptap_to_markdown(job["summary"])

        # Build markdown
        md = build_markdown(job, detail_sections)

        # Generate filename
        fname = sanitize_filename(f"{company} - {title}") + ".md"
        fpath = os.path.join(args.output_dir, fname)

        if args.dry_run:
            results["created"].append(fname)
        else:
            with open(fpath, "w") as f:
                f.write(md)
            results["created"].append(fname)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
