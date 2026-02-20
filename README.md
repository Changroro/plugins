# cc-plugins-bch

<div align="center">

**Claude Code 플러그인 컬렉션**<br/>
문서 자동 생성, Git 워크플로우, 코드 리뷰, 뉴스 수집 등 개발 반복 작업을 자동화합니다

[![Release](https://img.shields.io/github/v/release/Bae-ChangHyun/cc-plugins-bch?style=flat-square&color=blue)](https://github.com/Bae-ChangHyun/cc-plugins-bch/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](#)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-8A2BE2?style=flat-square)](https://github.com/anthropics/claude-code)
[![Plugins](https://img.shields.io/badge/Plugins-5-green?style=flat-square)](#-플러그인-목록)

[설치하기](#-설치) • [플러그인 목록](#-플러그인-목록) • [사용 예시](#-사용-예시)

</div>

---

## 설치

```bash
# 1. 마켓플레이스 등록
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch

# 2. 플러그인 설치
/plugin install docs@cc-plugins-bch        # 문서 작성
/plugin install dev@cc-plugins-bch         # 개발 지원
/plugin install gitwf@cc-plugins-bch       # Git/GitHub 워크플로우
/plugin install utils@cc-plugins-bch       # 개발 유틸리티
/plugin install newsletter@cc-plugins-bch  # 뉴스 수집
```

<details>
<summary><strong>MCP Servers 설정 (docs, dev 플러그인 사용 시)</strong></summary>

```bash
# Playwright - 웹 페이지 크롤링 (docs 플러그인)
npx @playwright/mcp@latest

# Context7 - 최신 라이브러리 문서 조회 (docs, dev 플러그인)
npx -y @upstash/context7-mcp

# Obsidian (선택) - Obsidian 노트 연동 (docs 플러그인)
npx -y mcp-obsidian
```

</details>

---

## 플러그인 목록

| 플러그인 | 설명 | 주요 기능 |
|:---:|:---:|:---|
| **docs** | 문서 작성 자동화 | 블로그, 업무일지, 개발일지, 포트폴리오, README |
| **dev** | 개발 지원 | 코드 리뷰, 프로덕트 분석, 기술 스택 업데이트 |
| **gitwf** | Git 워크플로우 | Conventional Commits, PR 생성/병합/리뷰 |
| **utils** | 유틸리티 | 스킬 작성 가이드, OCR, 세션 마이그레이션 |
| **newsletter** | 뉴스 수집 | HN, Reddit, GeekNews 등 7개 소스 AI 뉴스 |

---

### docs - 문서 작성 자동화

블로그, 일지, README, 포트폴리오를 AI가 자동 생성합니다.

<details>
<summary>상세 보기</summary>

**Agents:**
- **blog-writer** - 기술 블로그 글 작성 (URL 참조, 웹 검색)
- **worklog-writer** - 업무일지 생성 (경영진 보고용)
- **devlog-writer** - 상세 개발일지 생성 (기술 상세)
- **portfolio-writer** - 포트폴리오 작성/업데이트
- **readme-architect** - README.md 작성/개선

**Commands:**
`/docs:blog` `/docs:worklog` `/docs:devlog` `/docs:portfolio` `/docs:readme` `/docs:configure`

**필요 MCP:** playwright, context7, mcp-obsidian(선택)

</details>

---

### dev - 개발 지원

코드 리뷰, 프로젝트 전략 분석, 기술 스택 최신화를 수행합니다.

<details>
<summary>상세 보기</summary>

**Agents:**
- **product-advisor** - 프로젝트 전략 분석 (개선점 제안, 기능 추천)
- **stack-updater** - 기술 스택 최신화 (최신 문서 조회, 베스트 프랙티스)
- **senior-code-reviewer** - 종합 코드 리뷰 (아키텍처, 기능, 비즈니스)

**Commands:**
`/dev:review` `/dev:advisor` `/dev:update-stack`

**필요 MCP:** playwright, context7

</details>

---

### gitwf - Git/GitHub 워크플로우

Conventional Commits 커밋, PR 생성/병합/리뷰를 자동 처리합니다.

<details>
<summary>상세 보기</summary>

**Skills:**
- **git-commit** - Conventional Commits + Emoji 자동 커밋 ("커밋해줘")
- **pr-create** - GitHub PR 생성 ("PR 만들어줘")
- **pr-merge** - GitHub PR 병합 ("PR 머지해줘")
- **pr-review** - PR 리뷰 코멘트 처리 ("리뷰 반영해줘")

**커밋 형식:**
```
✨ feat(auth): add JWT login validation
🐛 fix(api): resolve memory leak in parser
♻️ refactor(db): simplify query builder logic
```

</details>

---

### utils - 유틸리티

스킬 작성 가이드, OCR, 세션 마이그레이션 등 편의 기능입니다.

<details>
<summary>상세 보기</summary>

**Skills:**
- **creating-skills** - Claude Code 스킬 작성 가이드 ("스킬 만들어줘")
- **ocr** - PDF/이미지를 Vision OCR로 마크다운 변환 ("OCR", "PDF 변환")
- **session-migrate** - Claude Code 세션을 다른 프로젝트로 마이그레이션 ("세션 옮겨줘")

</details>

---

### newsletter - 뉴스 수집

AI/개발 관련 뉴스를 7개 소스에서 자동 수집하여 새 글만 전달합니다.

<details>
<summary>상세 보기</summary>

**Skills:**

| 스킬 | 소스 | 설명 |
|:---:|:---:|:---|
| **hn-news** | Hacker News | AI 관련 뉴스 필터링 (키워드 기반) |
| **reddit-news** | Reddit | AI 서브레딧 모니터링 (11개 subreddit) |
| **geeknews-news** | GeekNews | news.hada.io 새 글 수집 |
| **devday-news** | DevDay | devday.kr AI 섹션 수집 |
| **tldr-news** | TLDR | TLDR AI 뉴스레터 RSS 수집 |
| **threads-news** | Threads | AI 인플루언서 글 수집 (RSSHub) |
| **velopers-news** | Velopers | velopers.kr RSS 수집 |

- JSONL 기반 중복 제거, 30일 자동 정리
- Python 표준 라이브러리만 사용 (외부 의존성 없음)
- HN, Reddit, GeekNews는 점수 기반 정렬

</details>

---

## 데스크톱 알림 (Hooks)

모든 플러그인에 리눅스 데스크톱 알림이 포함되어 있습니다.

| 이벤트 | 알림 내용 | Urgency |
|--------|----------|---------|
| 권한 요청 | "권한 승인이 필요합니다" | critical |
| 입력 대기 | "입력을 기다리고 있습니다" | normal |
| 작업 완료 | "작업이 완료되었습니다" | normal |

```bash
# 리눅스 (대부분 기본 설치됨)
sudo apt install libnotify-bin

# macOS는 osascript 자동 사용
```

---

## 업데이트

```bash
/plugin marketplace update
/plugin update docs@cc-plugins-bch
/plugin update dev@cc-plugins-bch
/plugin update gitwf@cc-plugins-bch
/plugin update utils@cc-plugins-bch
/plugin update newsletter@cc-plugins-bch
```

---

## 라이센스

MIT License

---

<div align="center">

**Made with ❤️ by [Bae ChangHyun](https://github.com/Bae-ChangHyun)**

</div>
