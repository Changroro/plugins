---
name: ai-news-onboard
description: "AI 뉴스레터 초기 설정. 수집 플랫폼 선택, Telegram 봇 토큰, 수집 주기를 설정한다. 사용자가 '뉴스레터 설정', '뉴스 설정', 'onboard', '플랫폼 바꾸고 싶어', '텔레그램 연동', '수집 주기 변경' 등을 말하면 반드시 이 스킬을 사용할 것."
allowedTools:
  - "Bash(python3 *)"
---

# AI 뉴스레터 설정

인터랙티브 설정 스크립트를 실행한다. 스크립트가 사용자와 직접 대화하며 config.json을 생성한다.

```bash
python3 {PLUGIN_DIR}/scripts/onboard.py
```

스크립트 실행 후 추가 작업 없음. 결과를 사용자에게 전달하지 않아도 된다 (스크립트가 직접 출력).
