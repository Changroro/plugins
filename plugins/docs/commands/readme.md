---
description: Launch readme-architect agent to create/improve README.md (polished-readme 통합)
allowed-tools:
  - Read
  - Write
  - Bash(git *)
  - Bash(mkdir *)
  - Bash(cat *)
  - Bash(pwd)
  - Bash(ls *)
  - Bash(find *)
  - Glob
  - Grep
  - AskUserQuestion
---

# README Creation Flow

> **v2.0 변경 사항**: `polished-readme` 스킬이 이 커맨드로 흡수되었다. 배너 자동 생성(`scripts/build_banner.py`), 실제 스크린샷 캡처, 8단 OSS skeleton, Honesty principles가 readme-architect 에이전트 안에 들어있다. CLI/TUI 프로젝트는 `terminal-gif-maker` 스킬을 별도로 호출한다 (`/docs:readme`가 호출 가이드를 README에 임베드).

## Pre-check: Read Current Directory

```bash
# Get current directory
pwd
# 시각 자산 디렉토리 후보 빠른 스캔
find . -path ./node_modules -prune -o \
  \( -iname "icon*" -o -iname "logo*" -o -iname "mascot*" \
     -o -iname "screenshot*" -o -iname "banner*" -o -iname "*.gif" \) \
  -print 2>/dev/null | head -20
```

Store these values:
- `{current_directory}`: Current working directory
- `{current_project_name}`: basename of current directory
- `{visual_assets_present}`: 위 find 결과로 추정 (있음/없음)

## Step 1: Select Mode (작성 모드)

Use AskUserQuestion:

```
Question: "README를 어떤 방식으로 작성할까요?"
Header: "작성 모드"
Options:
  - label: "자동 모드 (권장)", description: "프로젝트를 분석하여 자동으로 README 생성. 질문 없음."
  - label: "토의 모드", description: "질의응답을 통해 함께 README 작성 (한줄 설명, 핵심 기능, 시각 자산 등)"
multiSelect: false
```

## Step 2: 프로젝트 타입 확인 (자동/토의 공통)

프로젝트 구조를 빠르게 분석한 뒤 (`package.json` / `pyproject.toml` / `Cargo.toml` / `Info.plist` / `app.json` / `next.config.*` 등의 존재 여부로 추정):

Use AskUserQuestion:

```
Question: "이 프로젝트의 타입은 무엇인가요? (감지된 타입: {detected_type})"
Header: "프로젝트 타입"
Options:
  - label: "CLI / TUI", description: "터미널 명령어/대화형 터미널 앱"
  - label: "Library / SDK", description: "다른 코드에서 import해서 쓰는 패키지"
  - label: "Native App", description: "iOS / Android / 데스크톱 앱"
  - label: "Web / Dashboard", description: "웹사이트, 대시보드, SPA"
multiSelect: false
```

(추가 옵션이 필요하면 사용자가 "Other"로 Data/Research 등 직접 입력 가능)

## Step 3: 시각 자산 옵션

프로젝트 타입에 따라 동적으로 옵션을 구성한다.

**프로젝트 타입 = App / Web**일 때:
```
Question: "README에 어떤 시각 자산을 포함할까요?"
Header: "시각 자산"
Options:
  - label: "배너 + 스크린샷 (권장)", description: "build_banner.py로 배너 생성 + 스크린샷 표"
  - label: "배너만", description: "polished 배너만"
  - label: "스크린샷만", description: "기존 스크린샷을 표로 정리"
  - label: "없음", description: "텍스트 + 배지만"
multiSelect: false
```

**프로젝트 타입 = CLI / TUI**일 때:
```
Question: "README에 어떤 시각 자산을 포함할까요?"
Header: "시각 자산"
Options:
  - label: "배너 + 데모 GIF (권장)", description: "배너 생성 + terminal-gif-maker 호출 안내"
  - label: "데모 GIF만", description: "terminal-gif-maker 스킬로 GIF만"
  - label: "없음", description: "텍스트 + 배지만 (명령어 표 위주)"
multiSelect: false
```

**프로젝트 타입 = Library / SDK**일 때:
```
Question: "README에 어떤 시각 자산을 포함할까요? (라이브러리는 일반적으로 배지+예시 위주)"
Header: "시각 자산"
Options:
  - label: "배지만 (권장)", description: "Shields.io 배지 + 코드 예시 위주, 시각 자산 생략"
  - label: "배너 + 배지", description: "브랜드가 있다면 배너도 추가"
  - label: "없음", description: "최소한의 텍스트 README"
multiSelect: false
```

**NOTE**:
- **CLI 옵션**에 "데모 GIF"가 들어가면 readme-architect가 README 내부에 `terminal-gif-maker` 호출 가이드와 임베드 placeholder를 삽입한다. 실제 GIF 생성은 사용자가 별도로 `"터미널 데모 GIF 만들어줘"`를 요청해야 한다 (다른 화면 녹화 도구 제안 금지 — VHS가 결정론적 기본값).
- **시각 자산이 없는 라이브러리/CLI**에는 placeholder를 강제로 채우지 않는다. 텍스트 우수성과 배지에 집중.

## Step 4: Launch Agent

After collecting selections, use the Task tool with subagent_type='readme-architect':

**Prompt format for agent:**
```
프로젝트 경로: [current_directory]
프로젝트 이름: [current_project_name]
작성 모드: [auto 또는 interactive]
프로젝트 타입: [CLI / Library / App / Web / Data / unknown]
시각 자산: [banner-and-gif / banner-and-screenshots / banner-only / screenshots-only / gif-only / badges-only / none]
추가 컨텍스트: $ARGUMENTS
```

자동 모드에서는 위 시각 자산이 `auto`로 들어가며, 에이전트가 프로젝트 분석으로 합리적 기본값을 결정한다 (사용자에게 다시 묻지 않음).

## Examples

**자동 모드 (App 프로젝트):**
```
User: /docs:readme

→ AskUserQuestion: 작성 모드?
   User: 자동 모드

→ AskUserQuestion: 프로젝트 타입? (감지: Native App)
   User: Native App

→ AskUserQuestion: 시각 자산?
   User: 배너 + 스크린샷

→ Task: readme-architect
   프로젝트 경로: /home/user/my-ios-app
   프로젝트 이름: my-ios-app
   작성 모드: auto
   프로젝트 타입: App
   시각 자산: banner-and-screenshots
```

**토의 모드 (CLI 프로젝트):**
```
User: /docs:readme

→ AskUserQuestion: 작성 모드?
   User: 토의 모드

→ AskUserQuestion: 프로젝트 타입? (감지: CLI)
   User: CLI / TUI

→ AskUserQuestion: 시각 자산?
   User: 배너 + 데모 GIF

→ Task: readme-architect
   프로젝트 경로: /home/user/my-cli
   프로젝트 이름: my-cli
   작성 모드: interactive
   프로젝트 타입: CLI
   시각 자산: banner-and-gif

→ readme-architect가 한줄 설명/핵심 기능/대상 사용자/설치 방법/추가 섹션 Q&A
→ README 초안 → 사용자 검토 → 최종 작성
→ 끝에 안내: "터미널 데모 GIF는 `terminal-gif-maker` 스킬을 호출하세요"
```

**Library 프로젝트:**
```
User: /docs:readme

→ AskUserQuestion: 작성 모드?
   User: 자동 모드

→ AskUserQuestion: 프로젝트 타입? (감지: Library)
   User: Library / SDK

→ AskUserQuestion: 시각 자산?
   User: 배지만

→ Task: readme-architect
   프로젝트 경로: /home/user/my-lib
   프로젝트 이름: my-lib
   작성 모드: auto
   프로젝트 타입: Library
   시각 자산: badges-only
```

**With context:**
```
User: /docs:readme 백엔드 라이브러리

→ AskUserQuestion: 작성 모드?
   User: 자동 모드

→ AskUserQuestion: 프로젝트 타입? (감지: Library)
   User: Library / SDK

→ AskUserQuestion: 시각 자산?
   User: 배지만

→ Task: readme-architect
   프로젝트 경로: /home/user/backend-lib
   프로젝트 이름: backend-lib
   작성 모드: auto
   프로젝트 타입: Library
   시각 자산: badges-only
   추가 컨텍스트: 백엔드 라이브러리
```
