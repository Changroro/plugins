#!/bin/bash
# 직행 필터 검색(전체 공고) 스크랩 - cron용
# crontab -e → 0 7 * * * /path/to/cron_search.sh
set -e

PLUGIN_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PARSE_SCRIPT="$PLUGIN_DIR/job-scraper/scripts/parse_jobs.py"
OUTPUT_DIR="/home/bch/obsidian_sync/개인/new_life/공고"
TMP_DIR="/tmp/zighang_search"
DETAIL_API="https://api.zighang.com/api/recruitments"
SEARCH_FILTER="depthTwos=AI%EC%84%9C%EB%B9%84%EC%8A%A4%EA%B8%B0%ED%9A%8D&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B6%84%EC%84%9D%EA%B0%80&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%82%AC%EC%9D%B4%EC%96%B8%ED%8B%B0%EC%8A%A4%ED%8A%B8&depthTwos=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EB%A8%B8%EC%8B%A0%EB%9F%AC%EB%8B%9D%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&depthTwos=%EC%83%9D%EC%84%B1%ED%98%95AI&depthTwos=%EC%98%81%EC%83%81_%EC%9D%8C%EC%84%B1AI&depthTwos=%EC%9E%90%EC%9C%A8%EC%A3%BC%ED%96%89&depthTwos=%EC%BB%B4%ED%93%A8%ED%84%B0%EB%B9%84%EC%A0%84&depthTwos=AI%EB%B9%84%EC%A6%88%EB%8B%88%EC%8A%A4&depthTwos=AI%EB%A6%AC%EC%84%9C%EC%B9%98&depthTwos=NLP&depthTwos=LLM&depthTwos=MLOps&depthTwos=RAG&depthTwos=%EA%B8%B0%ED%83%80AI_%EB%8D%B0%EC%9D%B4%ED%84%B0&careerMin=0&careerMax=2&employeeTypes=%EC%A0%95%EA%B7%9C%EC%A7%81&regions=%EC%84%9C%EC%9A%B8&regions=%EA%B2%BD%EA%B8%B0&educations=%EB%AC%B4%EA%B4%80&educations=%ED%95%99%EC%82%AC&sortCondition=ZIGHANG_SCORE&orderCondition=DESC"
SEARCH_API="https://api.zighang.com/api/recruitments/v2"

mkdir -p "$TMP_DIR"

# 1. headless 브라우저 열기
playwright-cli open https://zighang.com --persistent --browser=chrome 2>/dev/null

# 2. 인증 확인
AUTH=$(playwright-cli run-code "async page => { const r = await page.evaluate(async () => { const res = await fetch('https://api.zighang.com/api/users/me', {credentials:'include'}); return res.status; }); return r; }" 2>&1 | grep "^[0-9]" || echo "")

if [ "$AUTH" != "200" ]; then
    echo "ERROR: 인증 실패 (status: $AUTH). 수동 로그인 필요."
    playwright-cli close 2>/dev/null
    exit 1
fi

# 3. 총 개수 확인
TOTAL=$(playwright-cli run-code "async page => { const r = await page.evaluate(async () => { const res = await fetch('${SEARCH_API}?page=0&size=1&${SEARCH_FILTER}', {credentials:'include'}); const d = await res.json(); return d.data.totalElements; }); return r; }" 2>&1 | grep "^[0-9]" || echo "0")

echo "총 공고: ${TOTAL}개"
PAGES=$(( (TOTAL + 99) / 100 ))

# 4. 페이지별 수집
ALL_JOBS="[]"
for ((i=0; i<PAGES; i++)); do
    echo "페이지 $((i+1))/${PAGES} 수집 중..."

    playwright-cli run-code "async page => { const data = await page.evaluate(async () => { const r = await fetch('${SEARCH_API}?page=${i}&size=100&${SEARCH_FILTER}', {credentials:'include'}); const d = await r.json(); const jobs = d.data.content; for (const j of jobs) { try { const dr = await fetch('${DETAIL_API}/' + j.id, {credentials:'include'}); const dd = await dr.json(); j.summary = dd.data.summary || dd.data.content; } catch(e) {} } window.__page${i} = JSON.stringify(jobs); return jobs.length; }); return data + ' jobs'; }" 2>/dev/null

    playwright-cli eval "window.__page${i}" 2>&1 > "$TMP_DIR/page_${i}_raw.txt"
done

# 5. 브라우저 종료
playwright-cli close 2>/dev/null

# 6. 전체 JSON 합치기
python3 -c "
import json, glob
all_jobs = []
for f in sorted(glob.glob('${TMP_DIR}/page_*_raw.txt')):
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('\"['):
                data = json.loads(line)
                jobs = json.loads(data) if isinstance(data, str) else data
                all_jobs.extend(jobs)
                break
with open('${TMP_DIR}/all.json', 'w') as out:
    json.dump(all_jobs, out, ensure_ascii=False)
print(f'{len(all_jobs)} jobs total')
"

# 7. 마크다운 생성 (중복 체크)
cat "$TMP_DIR/all.json" | python3 "$PARSE_SCRIPT" --output-dir "$OUTPUT_DIR" --check-duplicates

# 8. 정리
rm -rf "$TMP_DIR"
