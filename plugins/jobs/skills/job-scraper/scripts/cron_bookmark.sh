#!/bin/bash
# 직행 북마크(관심공고) 스크랩 - cron용
# crontab -e → 0 7 * * * /path/to/cron_bookmark.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="/home/bch/obsidian_sync/개인/new_life/관심공고"
TMP_RAW="/tmp/zighang_bookmark_raw.txt"
TMP_JSON="/tmp/zighang_bookmark.json"
LIST_API="https://api.zighang.com/api/job-tracker?page=0&size=100"
DETAIL_API="https://api.zighang.com/api/recruitments"

# 1. headless 브라우저 열기 (persistent 프로필로 쿠키 재사용)
playwright-cli open https://zighang.com --persistent --browser=chrome 2>/dev/null

# 2. 인증 확인
AUTH=$(playwright-cli run-code "async page => { const r = await page.evaluate(async () => { const res = await fetch('${LIST_API}', {credentials:'include'}); return res.status; }); return r; }" 2>&1 | grep "^[0-9]" || echo "")

if [ "$AUTH" != "200" ]; then
    echo "ERROR: 인증 실패 (status: $AUTH). 수동 로그인 필요."
    playwright-cli close 2>/dev/null
    exit 1
fi

# 3. 목록 + 상세 수집
playwright-cli run-code "async page => { const data = await page.evaluate(async () => { const r = await fetch('${LIST_API}', {credentials:'include'}); const d = await r.json(); const jobs = d.data.content; for (const j of jobs) { try { const dr = await fetch('${DETAIL_API}/' + j.id, {credentials:'include'}); const dd = await dr.json(); j.summary = dd.data.summary || dd.data.content; } catch(e) {} } window.__data = JSON.stringify(jobs); return jobs.length; }); return data + ' jobs'; }" 2>/dev/null

# 4. 데이터 추출
playwright-cli eval "window.__data" 2>&1 > "$TMP_RAW"
playwright-cli close 2>/dev/null

# 5. escaped JSON 파싱
python3 -c "
import json
with open('${TMP_RAW}') as f:
    for line in f:
        line = line.strip()
        if line.startswith('\"['):
            data = json.loads(line)
            jobs = json.loads(data) if isinstance(data, str) else data
            with open('${TMP_JSON}', 'w') as out:
                json.dump(jobs, out, ensure_ascii=False)
            print(f'{len(jobs)} jobs parsed')
            break
"

# 6. 마크다운 생성 (중복 체크)
cat "$TMP_JSON" | python3 "$SCRIPT_DIR/parse_jobs.py" --output-dir "$OUTPUT_DIR" --check-duplicates

# 7. 정리
rm -f "$TMP_RAW" "$TMP_JSON"
