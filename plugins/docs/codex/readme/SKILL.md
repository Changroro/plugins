---
name: readme
description: 'Auto-generate a high-quality GitHub README.md. Detects project type (CLI/TUI, Library, Native App, Web/Dashboard, Data/Research), optionally generates a banner via build_banner.py, curates screenshots at 640px, embeds a terminal demo GIF placeholder for CLI projects, and writes an 8-section OSS-style README in Korean (or matches existing docs language). Trigger when the user says "README 만들어줘", "리드미 작성", "README 갱신", "README 새로 써줘", "create a README", "update README", or asks for README documentation of the current project.'
---

# README (Codex 판)

> 이 스킬은 **Codex CLI 전용 변환본**이다. Claude Code 판(`cc-plugins-bch/plugins/docs/skills/readme/`)과 동일한 동작을 하되, 배너 스크립트 경로와 데모 GIF 안내가 Codex 환경에 맞게 변환되어 있다.

현재 프로젝트를 분석해 GitHub용 README.md를 자동 생성한다. 사용자에게 모드/타입/시각 자산을 묻지 않고, 코드 신호로 합리적 기본값을 정한 뒤 바로 작성한다.

## 동작 원칙

- **묻지 않고 작성한다**. 프로젝트 타입, 시각 자산 여부는 신호로 결정.
- **실제 산출물 우선**. placeholder는 자산이 진짜 없을 때만.
- **언어**: 기존 docs와 매치. 없으면 한국어 기본.
- **정직하게**. 미구현 기능 약속 금지, 개인 프로젝트는 그렇다고 명시.

## Phase 0: 프로젝트 타입 판별

다음 신호로 타입을 결정한다.

| 타입 | 판별 신호 | README 전략 |
|---|---|---|
| **CLI / TUI** | `bin/`, `cmd/`, `package.json`의 `bin`, `setup.py`의 `console_scripts`, Cobra/Click/Typer/Clap, ncurses/Textual/blessed/charmbracelet | 배너(선택) + 데모 GIF 안내 + Quick Start + 명령어 표 |
| **Library / SDK** | `package.json`에 `main`/`exports`만 있고 `bin` 없음, `pyproject.toml`의 모듈 위주, npm/PyPI 패키지명 | 배지 + 빠른 사용 예시 + API 표 (배너/스크린샷 생략) |
| **Native App** | `Info.plist`, `Assets.xcassets/`, `app.json` (Expo), `AndroidManifest.xml`, `.xcodeproj/`, `Package.swift` | 배너(icon + phone mockup) + 시뮬레이터 스크린샷 표 + Features + Roadmap |
| **Web / Dashboard** | `next.config.*`, `vite.config.*`, `astro.config.*`, `app.vue`/`app.tsx`, `public/index.html`, 라이브 URL | 배너(card + browser mockup) + agent-browser 스크린샷 + Features + Tech stack |
| **Data / Research** | `notebooks/`, `data/`, `*.ipynb`, `requirements.txt`에 numpy/pandas/torch, 모델 weights | 방법론 + 데이터셋 + 결과 표/그래프 (배너 선택) |

판별이 모호하면 가장 가능성 높은 타입으로 진행하고, README 끝의 "후속 작업" 섹션에 수정 안내를 남긴다.

## Phase 1: Silent Analysis

질문 없이 조용히 수집:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/` 내용
- Manifest: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Info.plist`, `app.json`
- 디렉토리 구조 + 기술 스택 + git log로 활동성 확인
- Brand assets 광범위 탐색:
  ```bash
  find . -path ./node_modules -prune -o \
    \( -iname "*icon*" -o -iname "*logo*" -o -iname "*mascot*" \) -print
  ```
- 기존 스크린샷: `docs/`, `screenshots/`, `build/`, `ios-native/build/` — 직전 세션이 만들어 둔 일관된 세트가 있으면 우선 재사용

## Phase 2: 시각 자산 자동 결정

- 시각 표면(아이콘/마스코트/UI 스크린/라이브 URL)이 명확하면 → 배너 생성
- CLI/TUI → README에 데모 GIF 안내 박스 + placeholder 삽입 (실제 GIF는 VHS로 후속 생성)
- 순수 Library/SDK → 배너 생략, 배지 + 코드 예시 중심
- 시각 자산이 정말 없는 라이브러리/CLI는 placeholder를 강제로 채우지 않는다

## §A. Banner 생성

### A.1 언제 만드는가
- Native App / Web / Dashboard / 마케팅 사이트 / 명확한 아이콘이나 마스코트가 있는 도구
- 만들지 않는 경우: 순수 라이브러리, 시각 자산 없는 SDK, 일반 백엔드

### A.2 사전 결정

- **Theme**: 실제 앱/사이트 색을 샘플링해서 light/dark 결정. 피트니스/생산성/마케팅 → light, 다운로더/터미널/개발자 도구 → dark
- **Accent**: 프로젝트의 실제 brand accent. 아이콘 또는 primary CTA 색에서 추출
- **Wordmark split** (two-tone): 의미 있는 지점에서 끊기. `anything | down`, `health | gochi`, `super | base` (좋음) / `heal | thgochi` (나쁨)
- **Brand mark kind**:
  - `"icon"` — 앱 아이콘 PNG가 있을 때 (`Assets.xcassets/AppIcon.appiconset/Icon-1024.png`). ~112px 둥근 사각형
  - `"card"` — 아이콘 없고 마스코트만 있을 때. ~190×380 둥근 카드. 드롭 섀도 마스코트는 flood-fill 시 halo 생기므로 넉넉히 자른 직사각형을 카드로 쓰는 게 안전
- **Mockup kind**: `"phone"` (앱) / `"browser"` (웹/대시보드)
- **Pills**: 4개, 각 2-3단어. 리드 기능 라벨

### A.3 호출 방법

`scripts/build_banner.py`를 그대로 호출한다. inline 재구현 금지.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/readme/scripts/build_banner.py" /tmp/banner.json
```

> **폰트 주의 (Linux)**: `build_banner.py`는 기본적으로 macOS 시스템 폰트(`/System/Library/Fonts/SFNSRounded.ttf`, `SFNS.ttf`)를 사용한다. macOS가 아니면 해당 경로에 폰트가 없어 실패하므로, Linux/기타 환경에서는 (1) 배너 생성을 생략하고 README에 배너 placeholder를 남기거나, (2) 스크립트의 `ROUND`/`SANS` 폰트 경로를 설치된 TTF(예: `/usr/share/fonts/.../*.ttf`)로 바꿔 호출한다. 배너는 선택 기능이므로, 폰트가 없으면 무리하게 만들지 말고 placeholder로 진행한다.

config 예시:
```json
{
  "output": "docs/banner.png",
  "theme": "light",
  "accent": [232, 124, 42],
  "wordmark": ["health", "gochi"],
  "tagline": "LIFT · LOG · LEVEL UP",
  "description": [
    "A fast iOS workout logger wrapped in a",
    "tamagotchi-style growth loop."
  ],
  "pills": ["Workout logging", "Routines", "Pet growth", "Apple Health"],
  "brand_mark": { "path": "/tmp/tiger_card.png", "kind": "card" },
  "mockup":     { "path": "docs/screenshots/home.png", "kind": "phone" }
}
```

스크립트가 wordmark auto-fit, brand mark/mockup 배치, pills 충돌 방지를 처리한다. 결과를 보고 config를 조정한다 (pills overflow, wordmark 잘림 등).

저장 경로: `docs/banner.png`. 외부 호스팅 가정 금지.

## §B. 스크린샷 큐레이션

### B.1 무엇을 찍는가

4-6개: 홈/랜딩, 핵심 기능, 리스트/라이브러리 뷰, 시그니처 화면. 빈 상태 화면 피하기.

기존 dev 스크린샷이 다음 조건을 만족하면 그대로 사용:
- 같은 해상도 (예: 1179×2556 iPhone)
- 최신 UI (파일명에 `-refined-`, `-polish-`, `-final-`, 최신 timestamp)
- 콘텐츠가 채워진 상태

### B.2 640px 정규화

```python
from PIL import Image
W = 640
for name, src in chosen.items():
    im = Image.open(src).convert("RGB")
    H = round(im.height * W / im.width)
    im.resize((W, H), Image.LANCZOS).save(f"docs/screenshots/{name}.png")
```

### B.3 2-column 표

```markdown
| Home | Workout |
| :--: | :--: |
| ![Home](docs/screenshots/home.png) | ![Workout](docs/screenshots/workout.png) |
| **Routines** | **Calendar** |
| ![Routines](docs/screenshots/routines.png) | ![Calendar](docs/screenshots/calendar.png) |
```

### B.4 캡처 방법 — 프로젝트 타입별

**iOS / Android Native App**
- iOS Simulator: `xcrun simctl io <device-id> screenshot <out.png>`. 깊은 네비게이션은 앱 측에 `SIMCTL_CHILD_*` 환경변수 훅을 두고 화면으로 직접 이동한 뒤 캡처
- Android: `adb exec-out screencap -p > out.png`

**Web / Dashboard**

`agent-browser` CLI 사용:

```bash
agent-browser open https://the-site.example
agent-browser set viewport 1280 1800
agent-browser screenshot docs/screenshots/home.png
agent-browser open https://the-site.example/dashboard
agent-browser set viewport 1280 1800
agent-browser screenshot docs/screenshots/dashboard.png
agent-browser close
```

agent-browser가 없으면 headless Chrome:
```bash
chromium --headless --hide-scrollbars --window-size=1280,1800 \
  --screenshot=docs/screenshots/home.png "https://the-site.example"
```

사용자가 명시한 URL만 방문. 사이트 크롤링 금지.

## §C. 데모 GIF (CLI/TUI 전용)

CLI/TUI 프로젝트면 README에 다음과 같은 안내 + placeholder를 둔다:

```markdown
## 데모

<!--
TODO: 터미널 데모 GIF
- 생성 방법: VHS(charmbracelet/vhs)로 demo/main.tape 작성 후 `vhs demo/main.tape` 실행 (결정론적·재현 가능)
- 산출물: demo/main.gif, demo/main.tape (테이프도 커밋해야 재생성 가능)
- 임베드: <img src="demo/main.gif" alt="demo" width="780"/>
-->

<img src="demo/main.gif" alt="demo" width="780"/>
```

이 스킬은 직접 GIF를 만들지 않는다. GIF가 필요하면 VHS(`.tape`)로 생성한다 — 결정론적·CI 재현 가능해 README 임베드에 적합하다. asciinema/OBS/화면 녹화 같은 비결정론적 대안은 피한다. (Claude Code 환경에서는 `terminal-gif-maker` 스킬이 이 VHS 워크플로우를 자동화하지만, Codex에는 해당 스킬이 없으므로 `vhs`를 직접 호출한다.)

## 표준 README skeleton (8단)

```markdown
<div align="center">

![{name}](docs/banner.png)

**한 문장 핵심 가치 제안.**
두 번째 문장으로 unique angle 보강.

[![Release](https://img.shields.io/github/v/release/[User]/[Repo]?style=flat-square&color=blue)](https://github.com/[User]/[Repo]/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-iOS%20%7C%20macOS-orange?style=flat-square)](#)
[![Stack](https://img.shields.io/badge/Built%20with-Swift-blueviolet?style=flat-square)](#)
[![Status](https://img.shields.io/badge/Status-Personal--use-lightgrey?style=flat-square)](#)

[Download](#) • [Documentation](#)

</div>

---

> **⚠️ 참고**
> 개인 사용 / 개발 중 / 외부 서비스 의존 등 사용자에게 먼저 알려야 할 사항.

---

## 프로젝트 소개

한 문단 또는 두 문단. 이게 무엇이고, 누구를 위한 것이며, 다른 솔루션과 무엇이 다른가. 이름에 사연이 있으면 언급. 플랫폼과 핵심 기술 명시.

### 💡 이 프로젝트가 필요한 이유

- **문제**: 기존에 겪던 불편을 한 문장으로
- **해결**: 이 프로젝트가 어떻게 풀었는지 한 문장으로

---

## 스크린샷

(2-column 표, 2-3 row, 각 페어 위에 라벨)

또는 CLI/TUI면 이 자리에 데모 GIF:

<img src="demo/main.gif" alt="demo" width="780"/>

---

## 📊 Comparison (선택)

| 항목 | 이 프로젝트 | 경쟁 A |
|:---:|:---:|:---:|
| **비용** | **무료** | 유료 |
| **성능** | 🚀 빠름 | 🐢 느림 |
| **핵심 기능** | ✅ | ❌ |

---

## ✨ 주요 기능

기능을 2-3개 thematic bucket으로 묶는다 (flat 20-item list 금지).

### 코어
* **<짧은 라벨>**: 한 문장 설명
* **<짧은 라벨>**: 한 문장 설명

### 부가
* **<짧은 라벨>**: 한 문장 설명

---

## 작동 방식

짧은 ASCII flow + 설명 한 단락.

```
   Step 1            →     Step 2            →     Step 3
   (사용자 행동)            (앱 처리)              (결과)
```

---

## 🛠️ 기술 스택

- **앱**: 메인 프레임워크 + 언어
- **백엔드**: 있으면
- **주요 라이브러리**: 3-6개 (package.json 전부 X)

---

## 🚀 시작하기

### Prerequisites

```bash
# 실제로 존재하는 의존성 설치 명령
```

### Option 1: <메인 방법> (권장)

```bash
# copy-paste 가능한 명령
```

<details>
<summary><strong>고급 설치 옵션</strong></summary>

### Option 2: <대안 방법>

```bash
# 대안 설치
```

### Option 3: <소스 빌드>

```bash
# 빌드 명령
```

</details>

---

## 🗺️ 로드맵

3-7개 구체적/실행 가능 항목.

- [ ] 작업 1
- [ ] 작업 2
- [ ] 작업 3

---

## ⚠️ Status / Scope & Disclaimer

개인/프리릴리스/스코프 제한 프로젝트는 정직하게 마무리:

- 개인 사용 / 프리릴리스 / 활발한 개발 중
- 하지 **않는** 것 (DRM, 암호화 스트림, 소셜 등)
- 프로토타입 자산, 무보증, X와 무관

---

## 📄 라이선스

MIT License — `LICENSE` 참조.

---

<div align="center">
Made with ❤️ by [Developer Name]
</div>
```

### 프로젝트 타입별 skeleton 조정

| 타입 | About | Screenshots/GIF | Features | How it works | Tech | Getting started | Roadmap | Status |
|---|---|---|---|---|---|---|---|---|
| **CLI / TUI** | 짧게 | 데모 GIF placeholder | 명령어 표 우선 | 짧은 ASCII flow | 최소화 | 패키지 매니저 + 첫 명령 | 짧게 | 선택 |
| **Library / SDK** | 강하게 (use case) | 생략 | 코드 예시 위주 | 입출력 흐름 | 의존성 / 호환성 | npm/pip 설치 + 5줄 예제 | 짧게 | 선택 |
| **Native App** | 한 단락 + 플랫폼 | 시뮬레이터 스크린샷 표 | 2-3 bucket | 사용자 흐름 | 프레임워크 + 백엔드 | 빌드/설치 | 길게 | 권장 |
| **Web / Dashboard** | 강하게 (가치) | agent-browser 스크린샷 표 | 2-3 bucket | 데이터 흐름 | 풀스택 | 데모 URL + 셀프호스팅 | 권장 | 선택 |
| **Data / Research** | 방법론 | 표/그래프 이미지 | 데이터셋 + 결과 | 파이프라인 | 모델 + 라이브러리 | 환경 + 재현 명령 | 선택 | 권장 |

## Voice / Tone

- **평이하고 자신감 있게**. 마케팅 fluff 금지 — "revolutionary", "seamless", 숫자 없는 "blazingly fast"
- **모든 문장이 독자의 인식을 바꿔야 한다**. 의미 없는 문장 금지
- **짧은 문단**. 불릿은 자리값을 해야 한다
- **언어**: 기본 한국어. 영문 docs 프로젝트면 영문
- 한국어 헤더는 자연스러운 명사형 사용 ("프로젝트 소개", "시작하기", "주요 기능")

## Honesty principles (비협상)

README는 독자와의 계약이다.

- **미구현 기능 약속 금지**. DRM / 암호화 스트림 / 소셜 / 모바일 sync 등이 아직 안 됐다면 Scope에 명시
- **현재와 미래를 구분**. 현재는 About/Features, 미래는 Roadmap
- **개인 프로젝트는 그렇다고 말한다**. "개인 사용", "App Store 미등록", "무보증", "X와 무관"
- **프로토타입 자산은 flag**. 마스코트/스프라이트가 placeholder면 Status에 명시
- **지어낸 통계 금지**. 유저 수/처리량/"production-ready" — 진짜일 때만

## Working Process

1. **Determine Language**: 기존 docs 언어와 매치. 없으면 한국어
2. **Extract & Organize**: 이름, 목적, 기능, 기술 스택, 설치 단계 식별
3. **Identify Gaps**: 누락된 critical 정보 (로고, 스크린샷, 링크, 라이선스)
4. **Map to Structure**: 8단 skeleton에 배치
5. **Enhance & Polish**:
   - 호소력 있는 tagline과 가치 제안 작성
   - section 헤더 이모지 적절히 (남용 금지)
   - Shields.io 배지 (flat-square)
   - 코드 블록은 언어 명시 + copy-paste 가능
   - 긴 콘텐츠는 `<details>`/`<summary>`로 접기
   - 시각 자산은 실제 산출물 우선
6. **Placeholders only when needed**: 시각 자산이 정말 없을 때만:
   - `<!-- TODO: 실제 배너로 교체 -->` 명시적 TODO 코멘트
   - 시각 자산 없는 library/CLI는 placeholder를 강제하지 말 것

## Quality Checklist

기본 7항:

- [ ] 첫 3초 안에 명확한 가치 제안
- [ ] 일관된 이모지/배지 스타일
- [ ] Copy-paste 가능한 Quick Start (실제로 존재하는 명령)
- [ ] 가능하면 여러 설치 방법
- [ ] syntax highlight 된 코드 블록
- [ ] 비교/구조화된 데이터는 표
- [ ] 긴 섹션은 `<details>`/`<summary>`

추가 13항:

1. 배너가 프로젝트의 진짜 아이콘/마스코트를 쓰는가 (stock art 금지)
2. 배너 pills가 mockup과 충돌하지 않고 wordmark가 잘리지 않는가
3. Two-tone wordmark가 의미 있는 지점에서 끊기는가
4. 모든 스크린샷이 같은 너비(640px)이고 콘텐츠가 채워졌는가
5. 스크린샷 표가 balanced (rows 짝수, 라벨이 각 페어 위에)인가
6. About이 unique angle을 설명하는가 (단순 "an app for X" 금지)
7. Features가 2-3 bucket으로 묶였는가 (flat 20-item list 금지)
8. "How it works"에 다이어그램 또는 명확한 시각 구조가 있는가
9. Getting-started 명령이 **실제로 동작**하고 참조 경로가 존재하는가
10. Roadmap 항목이 구체적이고 실행 가능한가
11. Status 섹션이 scope/개인 사용/프로토타입 자산/DRM에 대해 정직한가
12. README 언어가 프로젝트의 다른 docs와 일치하는가
13. "Coming soon" placeholder가 어디에도 없는가

## Commit cautiously

작업 트리 건드리기 전 `git status`. unrelated modifications가 있으면 `git add -A` 금지 — 다른 work-in-progress를 쓸어 담는다.

```bash
git add README.md docs/banner.png docs/screenshots/
```

mid-refactor면 README 파일만 commit하고 상황을 사용자에게 보고. 사용자 명시적 허가 없이 push 금지.

## Output

전달물:

1. **완성된 `README.md`** — 한국어 기본 (사용자 명시 외)
2. **변경 요약** — 어떤 섹션을 어떤 근거로 작성했는지
3. **체크리스트** — placeholder 이미지/링크 교체 필요 사항
4. **후속 작업 안내**:
   - 배너 생성이 필요했지만 자산이 부족했다면: `build_banner.py` config 작성 가이드
   - CLI 데모 GIF가 필요하면: VHS로 `demo/main.tape` 작성 후 `vhs demo/main.tape` 생성 (Claude Code 환경에서는 `terminal-gif-maker` 스킬 사용 가능)
   - 스크린샷 추가가 필요하면: 프로젝트 타입별 캡처 방법 안내
