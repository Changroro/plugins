# cc-plugins-bch

<div align="center">

**Claude Code 플러그인 컬렉션**<br/>
문서 자동 생성, Git 워크플로우, AI 뉴스레터, 채용 지원 등 개발 반복 작업을 자동화합니다

[![Release](https://img.shields.io/github/v/release/Bae-ChangHyun/cc-plugins-bch?style=flat-square&color=blue)](https://github.com/Bae-ChangHyun/cc-plugins-bch/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](#)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-8A2BE2?style=flat-square)](https://github.com/anthropics/claude-code)
[![Plugins](https://img.shields.io/badge/Plugins-5-green?style=flat-square)](#-플러그인-목록)

[설치하기](#-설치) • [플러그인 목록](#-플러그인-목록)

</div>

---

## 설치

```bash
# 1. 마켓플레이스 등록
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch

# 2. 플러그인 설치
/plugin install docs@cc-plugins-bch        # 문서 작성
/plugin install gitwf@cc-plugins-bch       # Git/GitHub 워크플로우
/plugin install utils@cc-plugins-bch       # 개발 유틸리티
/plugin install newsletter@cc-plugins-bch  # AI 뉴스레터
/plugin install jobs@cc-plugins-bch        # 채용 지원
```

---

## 플러그인 목록

| 플러그인 | 설명 | 주요 기능 |
|:---:|:---:|:---|
| **docs** | 문서 작성 자동화 | 블로그, 업무일지, 개발일지, 포트폴리오, README |
| **gitwf** | Git 워크플로우 | Conventional Commits, PR 생성/병합/리뷰 |
| **utils** | 유틸리티 | 스킬 작성 가이드, OCR, 세션 마이그레이션 |
| **newsletter** | AI 뉴스레터 | 7개 소스 자동 수집, 카테고리 분류, Telegram 전송 |
| **jobs** | 채용 지원 | 환경 초기화, 채용공고 크롤링, 리서치, 자소서, 면접 |

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

</details>

---

### gitwf - Git/GitHub 워크플로우

Conventional Commits 커밋, PR 생성/병합/리뷰를 자동 처리합니다.

<details>
<summary>상세 보기</summary>

**Skills:**
- **git-commit** - Conventional Commits + Emoji 자동 커밋
- **pr-create** - GitHub PR 생성
- **pr-merge** - GitHub PR 병합
- **pr-review** - PR 리뷰 코멘트 처리

</details>

---

### utils - 유틸리티

<details>
<summary>상세 보기</summary>

**Skills:**
- **creating-skills** - Claude Code 스킬 작성 가이드
- **ocr** - PDF/이미지를 Vision OCR로 마크다운 변환
- **session-migrate** - Claude Code 세션을 다른 프로젝트로 마이그레이션

</details>

---

### newsletter - AI 뉴스레터

7개 플랫폼에서 AI/개발 뉴스를 자동 수집하고, 카테고리별로 분류하여 Telegram으로 전송합니다.

<details>
<summary>상세 보기</summary>

**Skills:**

| 스킬 | 설명 |
|:---:|:---|
| **ai-news-onboard** | 초기 설정 (플랫폼, Telegram bot_token, 주기) |
| **ai-news-start** | 시스템 crontab에 자동 수집 등록 (세션 유지 불필요) |
| **ai-news-stop** | crontab에서 자동 수집 해제 |
| **ai-news-now** | 즉시 1회 수집 |

**수집 소스:** HN, Reddit, GeekNews, TLDR, Threads, Velopers, DevDay

**주요 특징:**
- 카테고리 자동 분류 (모델&리서치, 도구&오픈소스, 보안, 업계동향, 개발실무)
- 점수 기반 필터링 (HN/Reddit >= 3, GeekNews >= 5)
- 크로스소스 URL 중복 제거
- Telegram 하이퍼링크 전송 (MarkdownV2)
- 시스템 cron 기반 — PC만 켜져있으면 자동 실행
- `claude -p` 활용 — Claude Code 세션 유지 불필요

```bash
/newsletter:ai-news-onboard   # 최초 설정
/newsletter:ai-news-start     # 자동 수집 시작 (crontab 등록)
/newsletter:ai-news-stop      # 자동 수집 중단
/newsletter:ai-news-now       # 즉시 수집
```

</details>

---

### jobs - 채용 지원

채용공고 크롤링부터 자소서 작성, 퇴고, 면접 준비까지 전 과정을 지원합니다.

<details>
<summary>상세 보기</summary>

**Skills:**

| 스킬 | 설명 |
|:---:|:---|
| **init** | 폴더 구조 생성 (현재 디렉토리 기준) |
| **crawl** | 채용공고 URL 크롤링 → 마크다운 정리 |
| **research** | 기업분석 + 직무분석 에이전트 병렬 실행 |
| **write** | 문항 유형 자동 판별 → 자소서 2-3개 버전 생성 |
| **review** | 클리셰 검사, AI 티 제거, 일관성 검증, 표현 업그레이드 |
| **interview** | 1분 자기소개, 질문 100개, 모의면접 |

**워크플로우:**
```
init → crawl → research → write → review → interview
```

- 모든 경로 상대경로 (현재 디렉토리 기준)
- 16개 프롬프트 템플릿 내장

</details>

---

## 데스크톱 알림 (Hooks)

| 이벤트 | 알림 내용 | Urgency |
|--------|----------|---------|
| 권한 요청 | "권한 승인이 필요합니다" | critical |
| 입력 대기 | "입력을 기다리고 있습니다" | normal |
| 작업 완료 | "작업이 완료되었습니다" | normal |

---

## 업데이트

```bash
/plugin marketplace update
/plugin update docs@cc-plugins-bch
/plugin update gitwf@cc-plugins-bch
/plugin update utils@cc-plugins-bch
/plugin update newsletter@cc-plugins-bch
/plugin update jobs@cc-plugins-bch
```

---

## 라이센스

MIT License
