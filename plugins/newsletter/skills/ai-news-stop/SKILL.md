---
name: ai-news-stop
description: "AI 뉴스레터 자동 수집을 중단한다. 시스템 crontab에서 뉴스레터 스케줄을 제거한다. 사용자가 '뉴스레터 중단', '뉴스 그만', 'stop', '자동 수집 꺼줘', '뉴스 멈춰' 등을 말하면 이 스킬을 사용할 것."
allowedTools:
  - "Bash(crontab *)"
  - "Bash(grep *)"
---

# AI 뉴스레터 중단

시스템 crontab에서 뉴스레터 스케줄을 제거한다.

## 절차

### 1. 현재 등록 확인

```bash
crontab -l 2>/dev/null | grep "ai-news"
```

관련 항목이 없으면 → "등록된 뉴스레터 스케줄이 없습니다." 출력 후 종료.

### 2. crontab에서 제거

```bash
crontab -l 2>/dev/null | grep -v "# ai-news-newsletter" | grep -v "ai-news-now" > /tmp/crontab_backup.txt
crontab /tmp/crontab_backup.txt
```

### 3. 확인

```bash
crontab -l 2>/dev/null | grep "ai-news" || echo "뉴스레터 스케줄 제거 완료"
```

"뉴스레터 자동 수집이 중단되었습니다."

## 주의

뉴스레터와 관련 없는 cron 항목은 절대 건드리지 않는다.
