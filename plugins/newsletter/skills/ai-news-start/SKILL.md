---
name: ai-news-start
description: "AI 뉴스레터 자동 수집 시작. 설정된 주기에 따라 뉴스 수집 cron 스케줄을 등록."
---

# AI 뉴스레터 시작

## 실행 절차

### 1단계: 설정 확인

```bash
cat {PLUGIN_DIR}/.data/config.json
```

- 파일이 없으면 → "설정이 없습니다. 먼저 `ai-news-onboard`를 실행하세요." 출력 후 종료.

### 2단계: Cron 스케줄 등록

config.json에서 `schedule.cron` 값을 읽어 CronCreate 도구로 등록한다.

CronCreate 파라미터:
- **schedule**: config의 `schedule.cron` 값
- **skill**: `ai-news-now`
- **description**: `AI 뉴스레터 자동 수집 ({schedule.label})`

### 3단계: 시작 확인

사용자에게 아래 내용을 전달:
- 수집 플랫폼 목록
- 수집 주기
- Telegram 전송 여부
- "뉴스레터 자동 수집이 시작되었습니다."

## 금지 사항

- config.json을 수정하지 마라.
- 설정 없이 cron을 등록하지 마라.
