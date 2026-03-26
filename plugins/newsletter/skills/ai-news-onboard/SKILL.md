---
name: ai-news-onboard
description: "AI 뉴스레터 초기 설정. 수집 플랫폼 선택, Telegram 봇 토큰, 수집 주기를 설정한다. 사용자가 '뉴스레터 설정', '뉴스 설정', 'onboard', '플랫폼 바꾸고 싶어', '텔레그램 연동', '수집 주기 변경' 등을 말하면 반드시 이 스킬을 사용할 것."
allowedTools:
  - "AskUserQuestion"
  - "Bash(curl -s *)"
  - "Bash(mkdir -p *)"
  - "Bash(cat *)"
  - "Read"
  - "Write"
---

# AI 뉴스레터 설정

config.json을 생성/업데이트한다. 아래 단계를 순서대로 진행한다.

## 1단계: 기존 설정 로드

```bash
cat {PLUGIN_DIR}/.data/config.json 2>/dev/null
```

## 2단계: 플랫폼 선택 (2회로 나누어 질문)

**첫 번째 질문 — 글로벌 소스:**

AskUserQuestion 도구로 묻는다. 반드시 아래 4개를 모두 보여줘야 한다:

- question: "수집할 글로벌 플랫폼을 선택하세요"
- options: ["HN (Hacker News)", "Reddit", "TLDR", "Threads (RSSHub 필요)"]
- multiSelect: true
- defaultValue: ["HN (Hacker News)", "Reddit", "TLDR", "Threads (RSSHub 필요)"]

매핑: HN=hn, Reddit=reddit, TLDR=tldr, Threads=threads

**두 번째 질문 — 국내 소스:**

AskUserQuestion 도구로 묻는다. 반드시 아래 3개를 모두 보여줘야 한다:

- question: "수집할 국내 플랫폼을 선택하세요"
- options: ["GeekNews (news.hada.io)", "Velopers (velopers.kr)", "DevDay (devday.kr)"]
- multiSelect: true
- defaultValue: ["GeekNews (news.hada.io)", "Velopers (velopers.kr)", "DevDay (devday.kr)"]

매핑: GeekNews=geeknews, Velopers=velopers, DevDay=devday

두 응답을 합쳐서 platforms 배열을 만든다.

## 3단계: 플랫폼별 상세 설정

**Reddit 선택 시** — AskUserQuestion:
- question: "Reddit 서브레딧을 변경할까요? (기본: Anthropic, ClaudeAI, LocalLLaMA 등 11개)"
- options: ["기본값 사용", "직접 입력"]

"직접 입력" 선택 시 추가 질문으로 서브레딧 목록을 받는다.
기본값: Anthropic, ArtificialInteligence, ClaudeAI, GithubCopilot, LocalLLaMA, ollama, OpenAI, openclaw, opensource, Qwen_AI, Vllm

**Threads 선택 시** — AskUserQuestion:
- question: "Threads RSSHub URL을 입력하세요 (예: http://localhost:1200). 없으면 '없음' 선택"
- options: ["없음"]

"없음" 선택 시 platforms에서 threads를 제거한다. 텍스트 입력이 있으면 rsshub_url로 저장.

## 4단계: Telegram 설정

AskUserQuestion:
- question: "Telegram으로 뉴스를 전송할까요?"
- options: ["예", "아니오"]

"예" 선택 시:

AskUserQuestion:
- question: "Telegram Bot 토큰을 입력하세요 (@BotFather에서 /newbot으로 발급)"

토큰을 받으면 chat_id를 조회한다. 다른 세션에서 Telegram 채널이 polling 중이면 getUpdates가 빈 결과를 반환하므로, 실패 시 직접 입력을 받는다.

1. 사용자에게 안내: "Telegram에서 봇에게 아무 메시지를 보내주세요"
   AskUserQuestion:
   - question: "Telegram에서 봇에게 아무 메시지를 보내주세요 (chat_id 조회에 필요합니다). 보내셨으면 '완료', chat_id를 이미 알고 있으면 직접 입력하세요."
   - options: ["완료"]

2. "완료" 선택 시 chat_id 조회:
```bash
curl -s "https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('result'):
    print(data['result'][-1]['message']['chat']['id'])
else:
    print('NO_UPDATES')
"
```

3. chat_id를 얻으면 확인: "chat_id: {값} — 맞나요?"

4. NO_UPDATES이면 → 테스트 메시지로 검증 시도:
```bash
curl -s -X POST "https://api.telegram.org/bot{TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "USER_INPUT", "text": "뉴스레터 설정 테스트"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('OK' if data.get('ok') else 'FAILED')
"
```
   AskUserQuestion으로 chat_id를 직접 입력받고, 위 테스트 메시지로 검증한다.
   - question: "chat_id 자동 조회에 실패했습니다 (다른 세션에서 봇을 사용 중일 수 있습니다). chat_id를 직접 입력하세요."
   - OK → "테스트 메시지를 보냈습니다. Telegram에서 확인하세요."
   - FAILED → "잘못된 chat_id입니다. 다시 입력하세요."

## 5단계: 수집 주기

AskUserQuestion:
- question: "수집 주기를 선택하세요"
- options: ["30분마다", "1시간마다", "2시간마다", "매일 09:00 KST"]
- defaultValue: ["1시간마다"]

매핑: 30분마다=`*/30 * * * *`, 1시간마다=`0 * * * *`, 2시간마다=`0 */2 * * *`, 매일=`0 0 * * *`

## 6단계: 저장

```bash
mkdir -p {PLUGIN_DIR}/.data
```

`{PLUGIN_DIR}/.data/config.json`에 저장:
```json
{
  "platforms": ["hn", "reddit", "geeknews", "tldr", "velopers", "devday"],
  "subreddits": ["Anthropic", "ClaudeAI"],
  "threads_accounts": ["choi.openai", "claudeai", "programmingzombie", "feelfree_ai"],
  "rsshub_url": "http://localhost:1200",
  "telegram": {
    "enabled": true,
    "bot_token": "123:AAH...",
    "chat_id": "123456789"
  },
  "schedule": { "cron": "0 * * * *", "label": "1시간마다" }
}
```

선택하지 않은 플랫폼 관련 필드는 생략한다. 저장 후 설정 요약을 보여준다.
