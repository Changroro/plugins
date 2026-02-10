---
name: job-scraper
description: 직행(zighang.com) 북마크 공고를 API로 스크랩하여 옵시디언 문서로 저장. Use when user wants to scrape job postings, 공고 스크랩, 직행 북마크 정리, 채용공고 저장. playwright headless로 쿠키 인증 유지하여 API 호출.
allowed-tools:
  - Bash(playwright-cli *)
  - Bash(cat * parse_jobs.py *)
  - Bash(python3 *)
  - Write
  - Read
---

# Job Scraper

직행 북마크 공고를 API로 수집하여 `/home/bch/obsidian_sync/개인/new_life/관심공고/`에 마크다운으로 저장.

## Quick Start

```bash
/job-scraper
```

## Core Workflow

### Step 1: headless 브라우저 열기 + 인증 확인

```bash
playwright-cli open https://zighang.com --persistent --browser=chrome
```

```bash
playwright-cli run-code "async page => { const r = await page.evaluate(async () => { const res = await fetch('https://api.zighang.com/api/users/me', {credentials:'include'}); return res.status; }); return r; }"
```

**200이면** Step 2로. **아니면** headed로 재로그인:

```bash
playwright-cli close
playwright-cli open https://zighang.com --headed --persistent --browser=chrome
# AskUserQuestion으로 로그인 완료 확인
```

### Step 2: 데이터 수집

```bash
playwright-cli run-code "async page => { const data = await page.evaluate(async () => { const r = await fetch('https://api.zighang.com/api/job-tracker?page=0&size=100', {credentials:'include'}); const d = await r.json(); const jobs = d.data.content; for (const j of jobs) { try { const dr = await fetch('https://api.zighang.com/api/recruitments/' + j.id, {credentials:'include'}); const dd = await dr.json(); j.summary = dd.data.summary || dd.data.content; } catch(e) {} } window.__scrapedJobs = JSON.stringify(jobs); return jobs.length; }); return data + ' jobs fetched'; }"
```

### Step 3: 데이터 추출 + 브라우저 종료

```bash
playwright-cli eval "window.__scrapedJobs"
# 출력을 /tmp/jobs_raw.txt로 저장
playwright-cli close
```

eval 결과는 escaped JSON string이므로 파싱 필요:

```python
import json
with open('/tmp/jobs_raw.txt') as f:
    for line in f:
        line = line.strip()
        if line.startswith('"['):
            data = json.loads(line)
            jobs = json.loads(data) if isinstance(data, str) else data
            with open('/tmp/scraped_jobs.json', 'w') as out:
                json.dump(jobs, out, ensure_ascii=False)
            break
```

### Step 4: 마크다운 생성

```bash
cat /tmp/scraped_jobs.json | python3 {SKILL_DIR}/scripts/parse_jobs.py --output-dir /home/bch/obsidian_sync/개인/new_life/관심공고/ --check-duplicates
```

마감 처리는 `parse_jobs.py`가 `endDate`를 확인하여 자동으로 `마감: 마감`을 설정함. 별도 후처리 불필요.

## Important Rules

- **ALWAYS** headless 우선, headed는 재로그인 시에만
- **ALWAYS** `run-code`는 `"async page => { ... }"` 형태로 호출
- **ALWAYS** 저장 경로: `/home/bch/obsidian_sync/개인/new_life/관심공고/`
- **NEVER** 기존 문서 삭제하지 않음
