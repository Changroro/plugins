# cc-plugins-bch

<div align="center">

![Claude Code Plugins](https://via.placeholder.com/150?text=CC+Plugins)

**프로덕션 레벨의 개발 자동화를 위한 Claude Code 플러그인 컬렉션**<br/>
문서 자동 생성부터 Git 워크플로우, 코드 리뷰까지 - 개발자의 반복 작업을 AI로 해결합니다

[![Release](https://img.shields.io/github/v/release/Bae-ChangHyun/cc-plugins-bch?style=flat-square&color=blue)](https://github.com/Bae-ChangHyun/cc-plugins-bch/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](#)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-8A2BE2?style=flat-square)](https://github.com/anthropics/claude-code)
[![Plugins](https://img.shields.io/badge/Plugins-4-green?style=flat-square)](#플러그인-목록)

[설치하기](#-설치) • [플러그인 목록](#-플러그인-목록) • [사용 예시](#-사용-예시)

</div>

---

> **이 프로젝트는 무엇인가요?**<br/>
> Claude Code 공식 마켓플레이스에서 사용 가능한 개인용 플러그인 저장소입니다. 실무에서 반복되는 문서 작성, Git 관리, 코드 리뷰 등의 작업을 자동화하는 4개의 플러그인을 제공합니다.

---

## 소개

**cc-plugins-bch**는 Claude Code의 확장성을 활용하여 개발 워크플로우를 최적화하는 플러그인 모음입니다.

### 이 프로젝트가 필요한 이유

- **문제:** 개발 중 반복되는 문서 작성(블로그, 일지, README), Git 커밋 메시지 포맷팅, 코드 리뷰 등에 시간을 낭비합니다
- **해결:** AI 에이전트가 프로젝트 분석, 문서 자동 생성, Conventional Commits 작성, 종합 코드 리뷰를 수행합니다
- **특징:** 각 플러그인은 독립적으로 설치 가능하며, MCP(Model Context Protocol) 서버와 통합되어 최신 문서 조회 및 브라우저 자동화를 지원합니다

### 배경

이 플러그인 컬렉션은 실제 개발 워크플로우에서 반복되는 패턴을 자동화하기 위해 만들어졌습니다. Claude Code의 Agents, Commands, Skills 시스템을 활용하여 단순 명령어가 아닌 "맥락을 이해하는 자동화"를 구현했습니다.

---

## 주요 기능

<div align="center">

| 플러그인 | 핵심 기능 | 자동화 작업 |
|:---:|:---:|:---:|
| **docs** | 문서 작성 자동화 | 블로그, 일지, README 생성 |
| **dev** | 개발 지원 | 코드 리뷰, 기술 스택 업데이트 |
| **gitwf** | Git 워크플로우 | Conventional Commits, PR 관리 |
| **utils** | 개발 도구 | 스킬 작성 가이드 |

</div>

### 핵심 강점

- **인터랙티브 입력 수집**: 사용자 친화적인 질문/옵션 선택으로 명령어 실행
- **컨텍스트 인식**: Git 커밋 분석, 프로젝트 구조 파악, 코드베이스 이해
- **멀티 소스 참조**: 웹 검색, URL 크롤링, 최신 문서 자동 조회 (Context7 MCP 연동)
- **결과물 품질 보장**: 기술 블로그는 실제 블로거 톤 학습, 커밋은 Conventional Commits 준수

---

## 설치

### 필수 요구사항

```bash
# Claude Code가 설치되어 있어야 합니다
# https://github.com/anthropics/claude-code
```

### 마켓플레이스 추가

```bash
# 1. 마켓플레이스 등록
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch
```

### 플러그인 설치

<details>
<summary><strong>전체 설치 (권장)</strong></summary>

```bash
/plugin install docs@cc-plugins-bch    # 문서 작성
/plugin install dev@cc-plugins-bch     # 개발 지원
/plugin install gitwf@cc-plugins-bch   # Git/GitHub 워크플로우
/plugin install utils@cc-plugins-bch   # 개발 유틸리티
```

</details>

<details>
<summary><strong>개별 설치</strong></summary>

필요한 플러그인만 선택적으로 설치할 수 있습니다:

```bash
# 문서 작성만 필요한 경우
/plugin install docs@cc-plugins-bch

# Git 워크플로우만 필요한 경우
/plugin install gitwf@cc-plugins-bch
```

</details>

---

## 플러그인 목록

### 1. docs 플러그인

문서 작성 관련 에이전트와 커맨드를 제공합니다.

#### Agents

| Agent | 설명 | 주요 기능 |
|-------|------|-----------|
| `blog-writer` | 기술 블로그 글 작성 | URL 참조, 웹 검색, 마크다운/HTML 출력 |
| `worklog-writer` | 업무일지 생성 (보고용) | git 커밋 분석, 경영진 보고 형식 |
| `devlog-writer` | 상세 개발일지 생성 | git 커밋 분석, 기술적 세부사항 기록 |
| `portfolio-writer` | 포트폴리오 작성/업데이트 | 프로젝트 분석, 기술 스택 정리 |
| `readme-architect` | README.md 작성/개선 | 오픈소스 베스트 프랙티스 적용 |

#### Commands

| Command | 설명 | 사용 예시 |
|---------|------|-----------|
| `/docs:blog` | 기술 블로그 글 작성 | `/docs:blog "MCP 프로토콜" https://example.com markdown` |
| `/docs:worklog` | 업무일지 생성 | `/docs:worklog` (인터랙티브 모드) |
| `/docs:devlog` | 상세 개발일지 생성 | `/docs:devlog` |
| `/docs:portfolio` | 포트폴리오 작성 | `/docs:portfolio` |
| `/docs:readme` | README 작성/개선 | `/docs:readme` |
| `/docs:configure` | 문서 저장 경로 설정 | `/docs:configure` |

#### 필요한 MCP Servers

| Server | 용도 | 설치 |
|--------|------|------|
| **playwright** | 웹 페이지 크롤링 | `npx @playwright/mcp@latest` |
| **context7** | 최신 라이브러리 문서 조회 | `npx -y @upstash/context7-mcp` |
| **mcp-obsidian** | Obsidian 노트 연동 (선택) | `npx -y mcp-obsidian` |

<details>
<summary><strong>블로그 작성 예시</strong></summary>

```bash
# 인터랙티브 모드 (질문 기반)
/docs:blog
→ 주제: FastAPI 시작하기
→ 참고 URL: https://fastapi.tiangolo.com
→ 형식: Markdown
→ 말투: 기술블로그 스타일
→ 저장 경로: docs/blog/

# Quick 모드 (인자 직접 전달)
/docs:blog "Docker 입문" https://docs.docker.com markdown

# 현재 프로젝트 기반 블로그 생성
/docs:blog
→ 주제 선택: "현재 프로젝트 기반" 선택
→ 프로젝트를 분석하여 자동으로 블로그 주제 및 내용 생성
```

</details>

---

### 2. dev 플러그인

개발 지원 관련 에이전트와 커맨드를 제공합니다.

#### Agents

| Agent | 설명 | 주요 기능 |
|-------|------|-----------|
| `product-advisor` | 프로젝트 전략 분석 | 개선점 제안, 기능 추천 |
| `stack-updater` | 기술 스택 최신화 | 최신 문서 조회, 베스트 프랙티스 적용 |
| `senior-code-reviewer` | 종합 코드 리뷰 | 아키텍처, 기능, 비즈니스 관점 |

#### Commands

| Command | 설명 | 사용 예시 |
|---------|------|-----------|
| `/dev:review` | 종합 코드 리뷰 | `/dev:review src/auth 모듈 보안 점검` |
| `/dev:advisor` | 프로덕트 어드바이저 | `/dev:advisor 현재 MVP 기능 검토` |
| `/dev:update-stack` | 기술 스택 업데이트 | `/dev:update-stack FastAPI` |

#### 필요한 MCP Servers

| Server | 용도 |
|--------|------|
| **playwright** | 웹 페이지 조작 |
| **context7** | 최신 라이브러리 문서 조회 |

<details>
<summary><strong>코드 리뷰 예시</strong></summary>

```bash
# 전체 프로젝트 리뷰
/dev:review

# 특정 모듈 리뷰
/dev:review src/auth 모듈 보안 점검

# 기술 스택 업데이트
/dev:update-stack FastAPI
→ FastAPI 최신 문서를 조회하여 deprecated API, 새로운 기능 적용 제안
```

</details>

---

### 3. gitwf 플러그인

Git/GitHub 워크플로우 자동화 스킬을 제공합니다.

#### Skills

| Skill | 설명 | 트리거 키워드 |
|-------|------|---------------|
| `git-commit` | Conventional Commits 형식 커밋 | "커밋해줘", "commit" |
| `pr-create` | GitHub PR 생성 | "PR 만들어줘", "pull request" |
| `pr-merge` | GitHub PR 병합 | "PR 머지해줘", "merge PR" |
| `pr-review` | PR 리뷰 코멘트 처리 | "리뷰 반영해줘", "apply review" |

#### git-commit 주요 특징

**Conventional Commits + Emoji 형식 자동 작성:**

```bash
# 형식: emoji type(scope): subject
✨ feat(auth): add JWT login validation
🐛 fix(api): resolve memory leak in parser
📝 docs(readme): update installation guide
♻️ refactor(db): simplify query builder logic
```

**핵심 원칙:**

- **기능 단위 커밋**: 관련 파일을 하나의 커밋으로 묶음 (파일별 커밋 X)
- **결과 중심 메시지**: 개발 과정이 아닌 최종 변경점만 기술
- **50+ 이모지 지원**: feat, fix, docs, refactor, test, chore 등

<details>
<summary><strong>커밋 타입 및 이모지 전체 목록</strong></summary>

| Emoji | Type | 설명 |
|-------|------|------|
| ✨ | `feat` | 새로운 기능 |
| 🐛 | `fix` | 버그 수정 |
| 📝 | `docs` | 문서 |
| 💄 | `style` | 포맷팅 (로직 변경 없음) |
| ♻️ | `refactor` | 리팩토링 |
| ⚡️ | `perf` | 성능 개선 |
| ✅ | `test` | 테스트 추가/수정 |
| 🔧 | `chore` | 도구, 설정 |
| 🚀 | `ci` | CI/CD |
| 🔒️ | `fix` | 보안 이슈 수정 |
| 🚑️ | `fix` | 긴급 핫픽스 |
| 🎨 | `refactor` | 구조/포맷 개선 |
| 🏗️ | `refactor` | 아키텍처 변경 |

[50+ 이모지 전체 목록 보기](/plugins/gitwf/skills/git-commit/SKILL.md)

</details>

#### pr-create 주요 특징

- 커밋 분석 및 타입/스코프 자동 추출
- 태스크 완료 검증 (tasks.md 체크)
- 테스트 실행 후 PR 생성
- 라벨 자동 제안

<details>
<summary><strong>PR 생성 예시</strong></summary>

```bash
# 1. 커밋 생성
git add .
커밋해줘
→ ✨ feat(auth): implement JWT login with refresh token

# 2. PR 생성
PR 만들어줘
→ 브랜치 분석, 커밋 히스토리 검토
→ 테스트 실행
→ PR 생성 (제목, 본문, 라벨 자동)
```

</details>

---

### 4. utils 플러그인

개발 유틸리티 스킬을 제공합니다.

#### Skills

| Skill | 설명 | 트리거 키워드 |
|-------|------|---------------|
| `creating-skills` | Claude Code 스킬 작성 가이드 | "스킬 만들어줘", "SKILL.md" |

#### creating-skills 주요 특징

**Claude Code 스킬 작성 공식 베스트 프랙티스:**

- SKILL.md 구조 및 프론트매터
- 네이밍 컨벤션 (lowercase-hyphen)
- 토큰 예산 관리 (< 500 lines)
- 헬퍼 스크립트 가이드라인
- 품질 체크리스트

---

## 사용 예시

### 프로젝트 기반 블로그 자동 생성

```bash
# 현재 프로젝트를 분석하여 블로그 글 작성
/docs:blog

→ 주제 선택: "프로젝트 기반" 선택
→ AI가 프로젝트 구조, README, 코드를 분석
→ 기술 스택, 핵심 기능, 사용 방법을 자동으로 블로그 형식으로 작성
→ 결과: docs/blog/{project_name}_소개_2025-01-07.md
```

### 코드 리뷰 후 Conventional Commits으로 커밋

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

### 최신 문서 조회로 기술 스택 업데이트

```bash
# FastAPI 최신 버전 반영
/dev:update-stack FastAPI

→ Context7 MCP로 FastAPI 최신 공식 문서 조회
→ deprecated API 탐지
→ 새로운 기능 및 Best Practice 적용 제안
→ 코드 수정 제안 (예: Pydantic v2 마이그레이션)
```

### 일주일 업무일지 자동 생성

```bash
/docs:worklog

→ 날짜 범위 선택: "지난 1주일"
→ git log 분석 (커밋 메시지, 변경 파일)
→ 경영진 보고용 포맷으로 정리
→ 결과: docs/worklog/2025-01-01_to_2025-01-07.md
```

---

## 업데이트

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

## 플러그인 구조

```
cc-plugins-bch/
├── plugins/
│   ├── docs/                # 문서 작성 플러그인
│   │   ├── .mcp.json       # MCP 서버 설정
│   │   ├── agents/         # 에이전트 정의
│   │   └── commands/       # 커맨드 정의
│   ├── dev/                # 개발 지원 플러그인
│   │   ├── .mcp.json
│   │   ├── agents/
│   │   └── commands/
│   ├── gitwf/              # Git 워크플로우 플러그인
│   │   └── skills/         # 스킬 정의
│   └── utils/              # 유틸리티 플러그인
│       └── skills/
└── README.md
```

---

## 설정

### MCP Servers 환경변수

```bash
# Obsidian 연동 (docs 플러그인)
export OBSIDIAN_API_KEY="your-obsidian-api-key"
```

### 문서 저장 경로 설정

```bash
# docs 플러그인 기본 경로 설정
/docs:configure

→ 기본 경로 입력: ~/Documents/docs/
→ 이후 문서 생성 시 이 경로를 기본값으로 사용
```

---

## 기여 및 라이센스

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

## 문의

- **GitHub Issues**: [프로젝트 이슈 페이지](https://github.com/Bae-ChangHyun/cc-plugins-bch/issues)
- **Author**: Bae ChangHyun

---

<div align="center">
Made with ❤️ by Bae ChangHyun
</div>
