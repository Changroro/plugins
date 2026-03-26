---
name: ai-news-now
description: "AI 뉴스를 지금 바로 수집한다. 7개 플랫폼(HN, Reddit, GeekNews, TLDR, Threads, Velopers, DevDay)에서 새 뉴스를 수집하고, 카테고리별로 분류하여 하이퍼링크 형식으로 전달한다. Telegram 설정이 되어있으면 카테고리별 메시지로 전송한다. 사용자가 '뉴스 보여줘', '지금 수집', 'now', '새 뉴스', 'AI 뉴스', '뉴스레터 한번만' 등을 말하면 이 스킬을 사용할 것. ai-news-start의 cron에 의해 자동 호출되기도 한다."
allowedTools:
  - "Agent"
  - "Bash(cat *)"
---

# AI 뉴스 즉시 수집

메인 컨텍스트를 보호하기 위해, 실제 수집/분류/전송 작업은 서브에이전트에게 위임한다.

## 실행

Agent 도구로 `news-collector` 서브에이전트를 실행한다:

- **subagent_type**: `news-collector`
- **prompt**: `PLUGIN_DIR={PLUGIN_DIR} 경로의 뉴스레터 플러그인에서 뉴스를 수집하고 전달하라.`
- **description**: `AI 뉴스 수집`

에이전트가 반환한 요약(한 줄)을 사용자에게 전달한다. 추가 설명이나 장황한 보고는 불필요하다.
