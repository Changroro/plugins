---
name: job-search
description: 직행(zighang.com) 채용공고를 필터 검색하여 옵시디언 문서로 저장. Use when user wants to search jobs, 공고 검색, AI 채용공고 수집, 직행 검색. 고정 필터(AI/데이터, 0~2년, 정규직, 서울/경기)로 검색.
allowed-tools:
  - Bash(playwright-cli *)
  - Bash(cat * parse_jobs.py *)
  - Bash(python3 *)
  - Write
  - Read
---

# Job Search

직행 채용공고 검색 API로 필터링된 공고를 수집하여 `공고/`에 저장.

## Quick Start

```bash
/job-search
```

## 고정 필터

| 항목 | 값 |
|------|-----|
| 직무 | AI/데이터 전 분야 (17개 카테고리) |
| 경력 | 0~2년 |
| 고용형태 | 정규직 |
| 지역 | 서울, 경기 |
| 학력 | 무관, 학사 |
| 정렬 | 직행 점수순 |

## Core Workflow

### Step 1: headless 브라우저 + 인증

```bash
playwright-cli open https://zighang.com --persistent --browser=chrome
```

```bash
playwright-cli run-code "async page => { const r = await page.evaluate(async () => { const res = await fetch('https://api.zighang.com/api/users/me', {credentials:'include'}); return res.status; }); return r; }"
```

**200이 아니면** headed로 재로그인 (`job-scraper` 스킬 Step 1 참조).

### Step 2: 총 공고 수 확인

```bash
playwright-cli run-code "async page => { const r = await page.evaluate(async () => { const res = await fetch('https://api.zighang.com/api/recruitments/v2?page=0&size=1&depthTwos=AI%EC%84%9C%EB%B9%84%EC%8A%A4%EA%B8%B0%ED%9A%8D&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B6%84%EC%84%9D%EA%B0%80&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%82%AC%EC%9D%B4%EC%96%B8%ED%8B%B0%EC%8A%A4%ED%8A%B8&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EC%83%9D%EC%84%B1%ED%98%95AI&depthTwos=%EC%98%81%EC%83%81_%EC%9D%8C%EC%84%B1AI&depthTwos=%EC%9E%90%EC%9C%A8%EC%A3%BC%ED%96%89&depthTwos=%EC%BB%B4%ED%93%A8%ED%84%B0%EB%B9%84%EC%A0%84&depthTwos=AI%EB%B9%84%EC%A6%88%EB%8B%88%EC%8A%A4&depthTwos=AI%EB%A6%AC%EC%84%9C%EC%B9%98&depthTwos=NLP&depthTwos=LLM&depthTwos=MLOps&depthTwos=RAG&depthTwos=%EA%B8%B0%ED%83%80AI_%EB%8D%B0%EC%9D%B4%ED%84%B0&careerMin=0&careerMax=2&employeeTypes=%EC%A0%95%EA%B7%9C%EC%A7%81&regions=%EC%84%9C%EC%9A%B8&regions=%EA%B2%BD%EA%B8%B0&educations=%EB%AC%B4%EA%B4%80&educations=%ED%95%99%EC%82%AC&sortCondition=ZIGHANG_SCORE&orderCondition=DESC', {credentials:'include'}); const d = await res.json(); return d.data.totalElements; }); return r; }"
```

총 개수로 페이지 수 계산: `Math.ceil(total / 100)`

### Step 3: 페이지별 병렬 수집

각 페이지를 별도 `page.evaluate`로 수집. 브라우저가 하나이므로 순차 실행하되, 각 페이지의 상세 API는 브라우저 내에서 병렬(`Promise.all`) 처리:

```bash
# 각 페이지(0, 1, 2, ...)에 대해 실행
playwright-cli run-code "async page => { const data = await page.evaluate(async () => { const r = await fetch('https://api.zighang.com/api/recruitments/v2?page={PAGE}&size=100&depthTwos=AI%EC%84%9C%EB%B9%84%EC%8A%A4%EA%B8%B0%ED%9A%8D&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B6%84%EC%84%9D%EA%B0%80&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%82%AC%EC%9D%B4%EC%96%B8%ED%8B%B0%EC%8A%A4%ED%8A%B8&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EC%83%9D%EC%84%B1%ED%98%95AI&depthTwos=%EC%98%81%EC%83%81_%EC%9D%8C%EC%84%B1AI&depthTwos=%EC%9E%90%EC%9C%A8%EC%A3%BC%ED%96%89&depthTwos=%EC%BB%B4%ED%93%A8%ED%84%B0%EB%B9%84%EC%A0%84&depthTwos=AI%EB%B9%84%EC%A6%88%EB%8B%88%EC%8A%A4&depthTwos=AI%EB%A6%AC%EC%84%9C%EC%B9%98&depthTwos=NLP&depthTwos=LLM&depthTwos=MLOps&depthTwos=RAG&depthTwos=%EA%B8%B0%ED%83%80AI_%EB%8D%B0%EC%9D%B4%ED%84%B0&careerMin=0&careerMax=2&employeeTypes=%EC%A0%95%EA%B7%9C%EC%A7%81&regions=%EC%84%9C%EC%9A%B8&regions=%EA%B2%BD%EA%B8%B0&educations=%EB%AC%B4%EA%B4%80&educations=%ED%95%99%EC%82%AC&sortCondition=ZIGHANG_SCORE&orderCondition=DESC', {credentials:'include'}); const d = await r.json(); const jobs = d.data.content; for (const j of jobs) { try { const dr = await fetch('https://api.zighang.com/api/recruitments/' + j.id, {credentials:'include'}); const dd = await dr.json(); j.summary = dd.data.summary || dd.data.content; } catch(e) {} } return JSON.stringify(jobs); }); return data; }"
```

각 페이지 결과를 `/tmp/search_page_{N}.json`에 저장 후 합침.

### Step 4: 마크다운 생성

```bash
cat /tmp/search_jobs_all.json | python3 {PLUGIN_DIR}/skills/job-scraper/scripts/parse_jobs.py --output-dir /home/bch/obsidian_sync/개인/new_life/공고/ --check-duplicates
```

`parse_jobs.py`는 `job-scraper` 스킬의 스크립트를 공유.

## Important Rules

- **ALWAYS** headless 우선
- **ALWAYS** `run-code`는 `"async page => { ... }"` 형태
- **ALWAYS** 저장 경로: `/home/bch/obsidian_sync/개인/new_life/공고/`
- **ALWAYS** `--check-duplicates`로 기존 문서와 중복 체크
- **NEVER** 기존 문서 삭제하지 않음
