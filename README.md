# cc-plugins-bch

<div align="center">

![Claude Code Plugins](https://via.placeholder.com/150?text=CC+Plugins)

**프로덕션 레벨의 개발 자동화를 위한 Claude Code 플러그인 컬렉션**<br/>
문서 자동 생성부터 Git 워크플로우, 코드 리뷰까지 - 개발자의 반복 작업을 AI로 해결합니다

[![Release](https://img.shields.io/github/v/release/Bae-ChangHyun/cc-plugins-bch?style=flat-square&color=blue)](https://github.com/Bae-ChangHyun/cc-plugins-bch/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](#)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-8A2BE2?style=flat-square)](https://github.com/anthropics/claude-code)
[![Plugins](https://img.shields.io/badge/Plugins-4-green?style=flat-square)](#-플러그인-목록)

[설치하기](#-설치) • [플러그인 목록](#-플러그인-목록) • [사용 예시](#-사용-예시)

</div>

---

> **💡 이 프로젝트는 무엇인가요?**<br/>
> Claude Code 공식 마켓플레이스에서 사용 가능한 개인용 플러그인 저장소입니다. 실무에서 반복되는 문서 작성, Git 관리, 코드 리뷰 등의 작업을 자동화하는 4개의 플러그인을 제공합니다.

---

## 📖 소개

**cc-plugins-bch**는 Claude Code의 확장성을 활용하여 개발 워크플로우를 최적화하는 플러그인 모음입니다.

### 💡 이 프로젝트가 필요한 이유

- **문제:** 개발 중 반복되는 문서 작성(블로그, 일지, README), Git 커밋 메시지 포맷팅, 코드 리뷰 등에 시간을 낭비합니다
- **해결:** AI 에이전트가 프로젝트 분석, 문서 자동 생성, Conventional Commits 작성, 종합 코드 리뷰를 수행합니다
- **특징:** 각 플러그인은 독립적으로 설치 가능하며, MCP(Model Context Protocol) 서버와 통합되어 최신 문서 조회 및 브라우저 자동화를 지원합니다

### 🎨 배경

이 플러그인 컬렉션은 실제 개발 워크플로우에서 반복되는 패턴을 자동화하기 위해 만들어졌습니다. Claude Code의 Agents, Commands, Skills 시스템을 활용하여 단순 명령어가 아닌 "맥락을 이해하는 자동화"를 구현했습니다.

---

## 📸 데모 및 아키텍처

<div align="center">
  <img src="https://via.placeholder.com/800x500?text=Claude+Code+Plugins+Demo" alt="Plugin Demo Screenshot" width="800"/>
  <br/>
  <em>Claude Code에서 플러그인 명령어 실행 예시</em>
</div>

<br/>

<div align="center">
  <img src="https://via.placeholder.com/700x400?text=Plugin+Architecture+Diagram" alt="Architecture Diagram" width="700"/>
  <br/>
  <em>플러그인 아키텍처: Agents, Commands, Skills, MCP Servers 통합 구조</em>
</div>

---

## 📊 비교표

| 기능 | cc-plugins-bch | 수동 작업 | 타 솔루션 |
|:---:|:---:|:---:|:---:|
| **커밋 메시지 생성** | ✅ Conventional Commits + Emoji 자동 | ❌ 수작업 | ⚠️ 템플릿만 제공 |
| **문서 자동 생성** | ✅ 블로그/README/일지 통합 | ❌ 수작업 | ⚠️ 단일 포맷만 |
| **프로젝트 분석** | ✅ Git + 코드베이스 자동 파싱 | ❌ 수작업 | ❌ 미지원 |
| **최신 문서 조회** | ✅ MCP Context7 통합 | ❌ 수동 검색 | ❌ 미지원 |
| **PR 자동화** | ✅ 생성/병합/리뷰 통합 | ❌ 수작업 | ⚠️ 생성만 지원 |
| **설치 및 사용** | ✅ 1줄 명령어 설치 | - | ⚠️ 복잡한 설정 |

---

## ✨ 주요 기능

<div align="center">

| 플러그인 | 핵심 기능 | 자동화 작업 |
|:---:|:---:|:---:|
| **📝 docs** | 문서 작성 자동화 | 블로그, 일지, README 생성 |
| **🛠️ dev** | 개발 지원 | 코드 리뷰, 기술 스택 업데이트 |
| **🔀 gitwf** | Git 워크플로우 | Conventional Commits, PR 관리 |
| **🔧 utils** | 개발 도구 | 스킬 가이드, OCR, 세션 마이그레이션 |

</div>

### 🚀 핵심 강점

- **🎯 인터랙티브 입력 수집**: 사용자 친화적인 질문/옵션 선택으로 명령어 실행
- **🧠 컨텍스트 인식**: Git 커밋 분석, 프로젝트 구조 파악, 코드베이스 이해
- **🌐 멀티 소스 참조**: 웹 검색, URL 크롤링, 최신 문서 자동 조회 (Context7 MCP 연동)
- **✅ 결과물 품질 보장**: 기술 블로그는 실제 블로거 톤 학습, 커밋은 Conventional Commits 준수
- **🔔 데스크톱 알림**: 작업 완료/권한 요청 시 리눅스 데스크톱 알림 (모든 플러그인 포함)

---

## 🔔 데스크톱 알림 (Hooks)

모든 플러그인에 **리눅스 데스크톱 알림**이 포함되어 있습니다.

### 알림 트리거

| 이벤트 | 알림 내용 | Urgency |
|--------|----------|---------|
| **권한 요청** | "권한 승인이 필요합니다" | critical (빨간색) |
| **입력 대기** | "입력을 기다리고 있습니다" | normal |
| **작업 완료** | "작업이 완료되었습니다" | normal |

### 요구사항

```bash
# 리눅스: notify-send (대부분 기본 설치됨)
sudo apt install libnotify-bin  # Ubuntu/Debian

# macOS: osascript 자동 사용 (별도 설치 불필요)
```

### 작동 방식

플러그인 설치 시 `hooks/hooks.json`이 자동으로 로드되어, Claude Code의 특정 이벤트에서 알림 스크립트가 실행됩니다.

```
plugins/*/
├── hooks/
│   └── hooks.json      # Hook 설정 (자동 로드)
└── scripts/
    └── notify.sh       # 알림 스크립트
```

---

## 🚀 설치

### 필수 요구사항

```bash
# Claude Code가 설치되어 있어야 합니다
# https://github.com/anthropics/claude-code
```

### 빠른 시작

```bash
# 1. 마켓플레이스 등록
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch

# 2. 전체 플러그인 설치 (권장)
/plugin install docs@cc-plugins-bch    # 문서 작성
/plugin install dev@cc-plugins-bch     # 개발 지원
/plugin install gitwf@cc-plugins-bch   # Git/GitHub 워크플로우
/plugin install utils@cc-plugins-bch   # 개발 유틸리티
```

<details>
<summary><strong>개별 플러그인 선택 설치</strong></summary>

필요한 플러그인만 선택적으로 설치할 수 있습니다:

```bash
# 문서 작성만 필요한 경우
/plugin install docs@cc-plugins-bch

# Git 워크플로우만 필요한 경우
/plugin install gitwf@cc-plugins-bch

# 개발 지원만 필요한 경우
/plugin install dev@cc-plugins-bch

# 유틸리티만 필요한 경우
/plugin install utils@cc-plugins-bch
```

</details>

<details>
<summary><strong>MCP Servers 설정 (docs, dev 플러그인 사용 시)</strong></summary>

일부 플러그인은 MCP(Model Context Protocol) 서버를 활용합니다:

```bash
# Playwright - 웹 페이지 크롤링 (docs 플러그인)
npx @playwright/mcp@latest

# Context7 - 최신 라이브러리 문서 조회 (docs, dev 플러그인)
npx -y @upstash/context7-mcp

# Obsidian (선택) - Obsidian 노트 연동 (docs 플러그인)
npx -y mcp-obsidian
```

MCP 서버 설정은 `.mcp.json` 파일에서 관리됩니다.

</details>

---

## 📦 플러그인 목록

### 1️⃣ docs 플러그인

**문서 작성 자동화** - 블로그, 일지, README, 포트폴리오를 AI가 자동 생성합니다.

<details>
<summary><strong>📖 제공 기능</strong></summary>

#### 🤖 Agents

- **blog-writer**: 기술 블로그 글 작성 (URL 참조, 웹 검색)
- **worklog-writer**: 업무일지 생성 (경영진 보고용)
- **devlog-writer**: 상세 개발일지 생성 (기술 상세)
- **portfolio-writer**: 포트폴리오 작성/업데이트
- **readme-architect**: README.md 작성/개선

#### ⚡ Commands

- `/docs:blog` - 기술 블로그 글 작성
- `/docs:worklog` - 업무일지 생성
- `/docs:devlog` - 상세 개발일지 생성
- `/docs:portfolio` - 포트폴리오 작성
- `/docs:readme` - README 작성/개선
- `/docs:configure` - 문서 저장 경로 설정

#### 🔌 필요한 MCP Servers

- **playwright**: 웹 페이지 크롤링
- **context7**: 최신 라이브러리 문서 조회
- **mcp-obsidian**: Obsidian 노트 연동 (선택)

</details>

---

### 2️⃣ dev 플러그인

**개발 지원** - 코드 리뷰, 프로젝트 전략 분석, 기술 스택 최신화를 자동으로 수행합니다.

<details>
<summary><strong>🛠️ 제공 기능</strong></summary>

#### 🤖 Agents

- **product-advisor**: 프로젝트 전략 분석 (개선점 제안, 기능 추천)
- **stack-updater**: 기술 스택 최신화 (최신 문서 조회, 베스트 프랙티스 적용)
- **senior-code-reviewer**: 종합 코드 리뷰 (아키텍처, 기능, 비즈니스 관점)

#### ⚡ Commands

- `/dev:review` - 종합 코드 리뷰
- `/dev:advisor` - 프로덕트 어드바이저
- `/dev:update-stack` - 기술 스택 업데이트

#### 🔌 필요한 MCP Servers

- **playwright**: 웹 페이지 조작
- **context7**: 최신 라이브러리 문서 조회

</details>

---

### 3️⃣ gitwf 플러그인

**Git/GitHub 워크플로우 자동화** - Conventional Commits 커밋, PR 생성/병합/리뷰를 자동으로 처리합니다.

<details>
<summary><strong>🔀 제공 기능</strong></summary>

#### 🎯 Skills

- **git-commit**: Conventional Commits + Emoji 형식 자동 커밋 ("커밋해줘")
- **pr-create**: GitHub PR 생성 ("PR 만들어줘")
- **pr-merge**: GitHub PR 병합 ("PR 머지해줘")
- **pr-review**: PR 리뷰 코멘트 처리 ("리뷰 반영해줘")

#### ✨ 주요 특징

**Conventional Commits + Emoji:**
```bash
✨ feat(auth): add JWT login validation
🐛 fix(api): resolve memory leak in parser
📝 docs(readme): update installation guide
♻️ refactor(db): simplify query builder logic
```

**핵심 원칙:**
- 기능 단위 커밋 (관련 파일을 하나의 커밋으로 묶음)
- 결과 중심 메시지 (최종 변경점만 기술)
- 50+ 이모지 지원

</details>

---

### 4️⃣ utils 플러그인

**개발 유틸리티** - 스킬 작성 가이드, OCR, 세션 마이그레이션 등 편의 기능을 제공합니다.

<details>
<summary><strong>🔧 제공 기능</strong></summary>

#### 🎯 Skills

- **creating-skills**: Claude Code 스킬 작성 가이드 ("스킬 만들어줘")
- **ocr**: PDF/이미지를 Vision OCR로 마크다운 변환 ("OCR", "PDF 변환")
- **session-migrate**: Claude Code 세션을 다른 프로젝트로 마이그레이션 ("세션 옮겨줘")

#### 주요 특징

**creating-skills:**
- SKILL.md 템플릿 자동 생성
- 네이밍 컨벤션 가이드
- 베스트 프랙티스 적용

**ocr:**
- PDF, 이미지 지원 (`.pdf`, `.png`, `.jpg` 등)
- Claude Vision API 사용
- 배치 처리 (3개 단위 병렬)
- PDF 저장 방식 선택 (통합/페이지별)

**session-migrate:**
- 세션 대화 기록 복사
- 최근 N개 세션 선택
- 경로 자동 변환
- 기존 세션 추가/덮어쓰기 선택

</details>

---

## 💻 사용 예시

### 📌 프로젝트 기반 블로그 자동 생성

```bash
# 현재 프로젝트를 분석하여 블로그 글 작성
/docs:blog

→ 주제 선택: "프로젝트 기반" 선택
→ AI가 프로젝트 구조, README, 코드를 분석
→ 기술 스택, 핵심 기능, 사용 방법을 자동으로 블로그 형식으로 작성
→ 결과: docs/blog/{project_name}_소개_2026-01-08.md
```

### 📌 코드 리뷰 후 Conventional Commits으로 커밋

```bash
# 1. 코드 리뷰 실행
/dev:review

→ 아키텍처, 코드 품질, 보안, 성능 등 종합 리뷰
→ 개선 사항 및 Best Practice 제안

# 2. 수정 후 커밋
커밋해줘

→ git diff 분석
→ 기능 단위로 파일 그룹화
→ Conventional Commits 형식으로 커밋 메시지 자동 생성
→ 결과: ✨ feat(api): implement rate limiting with Redis
```

### 📌 최신 문서 조회로 기술 스택 업데이트

```bash
# FastAPI 최신 버전 반영
/dev:update-stack FastAPI

→ Context7 MCP로 FastAPI 최신 공식 문서 조회
→ deprecated API 탐지
→ 새로운 기능 및 Best Practice 적용 제안
→ 코드 수정 제안 (예: Pydantic v2 마이그레이션)
```

### 📌 일주일 업무일지 자동 생성

```bash
/docs:worklog

→ 날짜 범위 선택: "지난 1주일"
→ git log 분석 (커밋 메시지, 변경 파일)
→ 경영진 보고용 포맷으로 정리
→ 결과: docs/worklog/2026-01-01_to_2026-01-08.md
```

---

## 🔄 업데이트

```bash
# 마켓플레이스 동기화
/plugin marketplace update

# 플러그인 업데이트
/plugin update docs@cc-plugins-bch
/plugin update dev@cc-plugins-bch
/plugin update gitwf@cc-plugins-bch
/plugin update utils@cc-plugins-bch
```

---

## 📂 플러그인 구조

```
cc-plugins-bch/
├── .claude-plugin/
│   └── marketplace.json      # 마켓플레이스 메타데이터
├── plugins/
│   ├── docs/                 # 문서 작성 플러그인
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json   # 플러그인 설정
│   │   ├── .mcp.json         # MCP 서버 설정
│   │   ├── hooks/            # 데스크톱 알림 Hook
│   │   │   └── hooks.json
│   │   ├── scripts/
│   │   │   └── notify.sh
│   │   ├── agents/           # 에이전트 정의
│   │   │   ├── blog-writer.md
│   │   │   ├── worklog-writer.md
│   │   │   ├── devlog-writer.md
│   │   │   ├── portfolio-writer.md
│   │   │   └── readme-architect.md
│   │   └── commands/         # 커맨드 정의
│   │       ├── blog.md
│   │       ├── worklog.md
│   │       ├── devlog.md
│   │       ├── portfolio.md
│   │       ├── readme.md
│   │       └── configure.md
│   ├── dev/                  # 개발 지원 플러그인
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── .mcp.json
│   │   ├── hooks/            # 데스크톱 알림 Hook
│   │   │   └── hooks.json
│   │   ├── scripts/
│   │   │   └── notify.sh
│   │   ├── agents/
│   │   │   ├── product-advisor.md
│   │   │   ├── stack-updater.md
│   │   │   └── senior-code-reviewer.md
│   │   └── commands/
│   │       ├── advisor.md
│   │       ├── review.md
│   │       └── update-stack.md
│   ├── gitwf/                # Git 워크플로우 플러그인
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── hooks/            # 데스크톱 알림 Hook
│   │   │   └── hooks.json
│   │   ├── scripts/
│   │   │   └── notify.sh
│   │   └── skills/           # 스킬 정의
│   │       ├── git-commit/
│   │       │   └── SKILL.md
│   │       ├── github-pr-creation/
│   │       │   └── SKILL.md
│   │       ├── github-pr-merge/
│   │       │   └── SKILL.md
│   │       └── github-pr-review/
│   │           └── SKILL.md
│   └── utils/                # 유틸리티 플러그인
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── hooks/            # 데스크톱 알림 Hook
│       │   └── hooks.json
│       ├── scripts/
│       │   └── notify.sh
│       └── skills/
│           ├── creating-skills/
│           │   └── SKILL.md
│           └── ocr/
│               └── SKILL.md
├── .gitignore
└── README.md
```

---

## ⚙️ 설정

### 환경변수 설정

<details>
<summary><strong>MCP Servers 환경변수</strong></summary>

```bash
# Obsidian 연동 (docs 플러그인)
export OBSIDIAN_API_KEY="your-obsidian-api-key"

# Context7 (선택, API 키 필요시)
export CONTEXT7_API_KEY="your-context7-api-key"
```

</details>

### 문서 저장 경로 설정

```bash
# docs 플러그인 기본 경로 설정
/docs:configure

→ 기본 경로 입력: ~/Documents/docs/
→ 이후 문서 생성 시 이 경로를 기본값으로 사용
```

---

## 🤝 기여 및 라이센스

### 기여하기

이슈 및 Pull Request를 환영합니다!

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-plugin`)
3. Commit your changes (`git commit -m '✨ feat(plugin): add amazing plugin'`)
4. Push to the branch (`git push origin feature/amazing-plugin`)
5. Open a Pull Request

### 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

---

## 📞 문의

- **GitHub Issues**: [프로젝트 이슈 페이지](https://github.com/Bae-ChangHyun/cc-plugins-bch/issues)
- **Author**: Bae ChangHyun
- **Repository**: [https://github.com/Bae-ChangHyun/cc-plugins-bch](https://github.com/Bae-ChangHyun/cc-plugins-bch)

---

## 🗺️ 로드맵

- [ ] **v1.1**: 추가 MCP 서버 통합 (Slack, Notion)
- [ ] **v1.2**: 다국어 지원 (영어, 일본어)
- [ ] **v2.0**: VSCode Extension 버전 출시
- [ ] **플러그인 추가**: AI 기반 테스트 자동 생성 플러그인

---

<div align="center">

**Made with ❤️ by Bae ChangHyun**

[⬆ 맨 위로 돌아가기](#cc-plugins-bch)

</div>
