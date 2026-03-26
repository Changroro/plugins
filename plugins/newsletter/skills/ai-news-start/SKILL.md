---
name: ai-news-start
description: "AI 뉴스레터 자동 수집을 시작한다. config.json의 주기 설정에 따라 시스템 crontab에 등록하여, PC가 켜져있는 동안 자동으로 뉴스를 수집하고 Telegram으로 전송한다. Claude Code 세션 유지가 필요 없다. 사용자가 '뉴스레터 시작', '뉴스 수집 시작', 'start', '자동 수집 켜줘', '뉴스 보내기 시작' 등을 말하면 이 스킬을 사용할 것."
allowedTools:
  - "Bash(cat *)"
  - "Bash(crontab *)"
  - "Bash(which claude)"
  - "Read"
---

# AI 뉴스레터 시작

시스템 crontab에 등록하여 PC가 켜져있는 한 자동 수집한다. Claude Code 세션 유지 불필요.

## 절차

### 1. 설정 확인

```bash
cat {PLUGIN_DIR}/.data/config.json 2>/dev/null
```

파일이 없으면 → "`/newsletter:ai-news-onboard`로 먼저 설정하세요." 안내 후 종료.

### 2. claude 경로 확인

```bash
which claude
```

### 3. crontab 등록

config.json의 `schedule.cron` 값으로 시스템 crontab에 등록한다.

기존 뉴스레터 cron이 있으면 먼저 제거 후 새로 등록한다:

```bash
crontab -l 2>/dev/null | grep -v "# ai-news-newsletter" | grep -v "ai-news-now" > /tmp/crontab_backup.txt
echo '{CRON_SCHEDULE} claude -p "/newsletter:ai-news-now" --plugin-dir {PLUGIN_DIR}/.. 2>/dev/null # ai-news-newsletter' >> /tmp/crontab_backup.txt
crontab /tmp/crontab_backup.txt
```

- `{CRON_SCHEDULE}`: config의 `schedule.cron` 값 (예: `0 * * * *`)
- `{PLUGIN_DIR}/..`: newsletter 플러그인의 부모 디렉토리 (plugins/)가 아니라 newsletter 디렉토리 자체를 가리켜야 한다. `--plugin-dir`에는 plugin.json이 있는 디렉토리의 경로를 넣는다.

### 4. 등록 확인

```bash
crontab -l | grep "ai-news"
```

사용자에게 전달:
- 수집 플랫폼 목록
- 수집 주기
- Telegram 전송 여부
- "뉴스레터가 시스템 cron에 등록되었습니다. PC가 켜져있으면 자동 실행됩니다."
- "중단하려면 `/newsletter:ai-news-stop`을 실행하세요."
