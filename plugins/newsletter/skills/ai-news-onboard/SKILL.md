---
name: ai-news-onboard
description: "AI 뉴스레터 초기 설정. 수집할 플랫폼, Telegram 전송, 수집 주기 등을 인터랙티브하게 설정."
---

# AI 뉴스레터 설정

사용자와 대화하며 뉴스레터 설정을 완료한다.

## 설정 절차

### 1단계: 플랫폼 선택

AskUserQuestion 도구로 수집할 플랫폼을 물어본다:

> 어떤 플랫폼에서 뉴스를 수집할까요? (번호로 선택, 콤마 구분. 예: 1,2,3)
>
> 1. HN (Hacker News) — AI 관련 글만 필터링
> 2. Reddit — AI 서브레딧에서 수집
> 3. GeekNews (news.hada.io)
> 4. TLDR — AI 뉴스레터 RSS
> 5. Threads — AI 인플루언서 글
> 6. Velopers (velopers.kr)
> 7. DevDay (devday.kr)
>
> 기본값: 전체 선택

플랫폼 이름 매핑: 1=hn, 2=reddit, 3=geeknews, 4=tldr, 5=threads, 6=velopers, 7=devday

### 2단계: Reddit 서브레딧 커스터마이징 (Reddit 선택 시)

Reddit을 선택한 경우에만:

> Reddit 서브레딧을 커스터마이징할까요?
> 기본값: Anthropic, ArtificialInteligence, ClaudeAI, GithubCopilot, LocalLLaMA, ollama, OpenAI, openclaw, opensource, Qwen_AI, Vllm
>
> 추가하거나 제거할 서브레딧이 있으면 알려주세요. 없으면 Enter.

### 3단계: Telegram 전송 설정

> Telegram으로 뉴스를 전송할까요? (y/n)

y인 경우:
> Telegram chat_id를 입력하세요:

### 4단계: 수집 주기 설정

> 수집 주기를 선택하세요:
> 1. 30분마다
> 2. 1시간마다 (기본값)
> 3. 2시간마다
> 4. 매일 (오전 9시 KST)

주기 매핑: 1="*/30 * * * *", 2="0 * * * *", 3="0 */2 * * *", 4="0 0 * * *"

### 5단계: 설정 저장

설정을 아래 형식으로 `{PLUGIN_DIR}/.data/config.json`에 저장:

```json
{
  "platforms": ["hn", "reddit", "geeknews"],
  "subreddits": ["Anthropic", "ClaudeAI", "LocalLLaMA"],
  "threads_accounts": ["choi.openai", "claudeai", "programmingzombie", "feelfree_ai"],
  "telegram": {
    "enabled": true,
    "chat_id": "123456789"
  },
  "schedule": {
    "cron": "0 * * * *",
    "label": "1시간마다"
  }
}
```

- `subreddits`: Reddit 미선택 시 필드 생략
- `threads_accounts`: Threads 미선택 시 필드 생략
- `telegram.enabled`: false이면 chat_id 필드 생략 가능

```bash
mkdir -p "$(dirname '{PLUGIN_DIR}/.data/config.json')"
```

저장 후 사용자에게 설정 요약을 보여준다.

## 금지 사항

- 사용자 응답 없이 기본값으로 진행하지 마라. 반드시 각 단계에서 확인을 받아라.
- config.json 외 다른 파일을 수정하지 마라.
