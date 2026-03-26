---
name: ai-news-onboard
description: "AI 뉴스레터 초기 설정 마법사. 수집 플랫폼 선택, Reddit 서브레딧/Threads RSSHub 등 플랫폼별 상세 설정, Telegram 전송 연동, 수집 주기를 인터랙티브하게 설정하고 config.json에 저장한다. 사용자가 '뉴스레터 설정', '뉴스 설정', 'onboard', '플랫폼 바꾸고 싶어', '텔레그램 연동', '수집 주기 변경' 등을 말하면 반드시 이 스킬을 사용할 것. 기존 설정을 변경하고 싶을 때도 이 스킬을 다시 실행하면 된다."
allowedTools:
  - "AskUserQuestion"
  - "Bash(curl -s *)"
  - "Bash(mkdir -p *)"
  - "Bash(cat *)"
  - "Read"
  - "Write"
---

# AI 뉴스레터 설정

사용자와 대화하며 config.json을 생성한다. 기존 설정 파일이 있으면 현재 값을 기본값으로 보여준다.

## 설정 흐름

### 1. 플랫폼 선택

기존 config.json이 있으면 먼저 읽어서 현재 설정을 파악한다:
```bash
cat {PLUGIN_DIR}/.data/config.json 2>/dev/null
```

AskUserQuestion으로 플랫폼을 물어본다:

> 수집할 플랫폼을 선택하세요 (번호, 콤마 구분. 예: 1,2,3)
>
> 1. HN (Hacker News) — AI 관련 글 필터링
> 2. Reddit — AI 서브레딧
> 3. GeekNews (news.hada.io)
> 4. TLDR — AI 뉴스레터 RSS
> 5. Threads — AI 인플루언서 (RSSHub 필요)
> 6. Velopers (velopers.kr)
> 7. DevDay (devday.kr)
>
> 기본값: 전체

매핑: 1=hn, 2=reddit, 3=geeknews, 4=tldr, 5=threads, 6=velopers, 7=devday

### 2. 플랫폼별 상세 설정

**Reddit 선택 시:**
> 서브레딧을 커스터마이징할까요?
> 기본: Anthropic, ArtificialInteligence, ClaudeAI, GithubCopilot, LocalLLaMA, ollama, OpenAI, openclaw, opensource, Qwen_AI, Vllm
>
> 변경할 내용이 있으면 알려주세요. 없으면 Enter.

**Threads 선택 시:**
> Threads는 RSSHub 서버가 필요합니다. URL을 입력하세요.
> (예: http://localhost:1200)
>
> RSSHub가 없으면 Enter → Threads를 플랫폼 목록에서 제외한다.

### 3. Telegram 전송 설정

> Telegram으로 뉴스를 전송할까요? (y/n)

**y인 경우:**

1. bot_token을 물어본다:
   > Telegram Bot 토큰을 입력하세요.
   > (@BotFather에서 /newbot으로 봇 생성 후 받은 토큰)
   >
   > 이미 설정한 적 있으면 Enter를 누르세요.

2. Enter(빈 입력)이면 기존 config.json의 `telegram.bot_token`을 사용한다. 기존 값도 없으면 "봇 토큰이 필요합니다" 안내.

3. bot_token을 받으면 자동으로 chat_id를 가져온다:
   ```bash
   curl -s "https://api.telegram.org/bot{TOKEN}/getUpdates" | python3 -c "
   import sys, json
   data = json.load(sys.stdin)
   if data.get('result'):
       print(data['result'][-1]['message']['chat']['id'])
   else:
       print('NO_UPDATES')
   "
   ```
   - chat_id 확인: "chat_id: {값} — 맞나요?"
   - `NO_UPDATES` → "봇에게 아무 메시지를 보낸 후 다시 시도하세요"

**빈 입력 또는 n** → telegram.enabled = false

### 4. 수집 주기

> 수집 주기를 선택하세요:
> 1. 30분 / 2. 1시간 (기본) / 3. 2시간 / 4. 매일 09:00 KST

매핑: 1=`*/30 * * * *`, 2=`0 * * * *`, 3=`0 */2 * * *`, 4=`0 0 * * *`

### 5. 저장

```bash
mkdir -p {PLUGIN_DIR}/.data
```

`{PLUGIN_DIR}/.data/config.json`에 저장:
```json
{
  "platforms": ["hn", "reddit", "geeknews"],
  "subreddits": ["Anthropic", "ClaudeAI"],
  "threads_accounts": ["choi.openai", "claudeai", "programmingzombie", "feelfree_ai"],
  "rsshub_url": "http://localhost:1200",
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:AAH...",
    "chat_id": "123456789"
  },
  "schedule": { "cron": "0 * * * *", "label": "1시간마다" }
}
```

선택하지 않은 플랫폼 관련 필드(subreddits, threads_accounts, rsshub_url)는 생략한다.

저장 후 설정 요약을 보여준다.

## 주의

- 각 단계에서 반드시 사용자 확인을 받는다. 기본값으로 넘어가지 않는다.
- config.json 외 파일을 수정하지 않는다.
