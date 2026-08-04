# changroro-plugins

<div align="center">

**창로로 — Claude Code 플러그인 마켓플레이스**<br/>
문서, 커밋, 채용, 뉴스, 코드 감사. 미루기 쉬운 일을 대신 처리한다.

[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](./LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-8A2BE2?style=flat-square)](https://github.com/anthropics/claude-code)
[![Plugins](https://img.shields.io/badge/Plugins-5-green?style=flat-square)](#플러그인)

</div>

---

## 설치

```bash
/plugin marketplace add Bae-ChangHyun/changroro-plugins

/plugin install docs@changroro-plugins        # 문서 작성
/plugin install gitwf@changroro-plugins       # Git/GitHub 워크플로우
/plugin install jobs@changroro-plugins        # 채용 지원
/plugin install newsletter@changroro-plugins  # AI 뉴스레터
/plugin install deep-audit@changroro-plugins  # 프로젝트 전수 감사
```

## 플러그인

각 플러그인은 독립된 저장소다. 마켓플레이스는 카탈로그 역할만 한다.

| 플러그인 | 하는 일 | 저장소 |
|---|---|---|
| **docs** | 블로그(Tistory), 업무일지, 개발일지, 포트폴리오, README, 세션 인계, 터미널 GIF | [changroro-docs](https://github.com/Bae-ChangHyun/changroro-docs) |
| **gitwf** | Conventional Commits 커밋, PR 생성·병합·리뷰 | [changroro-gitwf](https://github.com/Bae-ChangHyun/changroro-gitwf) |
| **jobs** | 채용공고 크롤링, 기업·직무 리서치, 자소서, 면접 준비 | [changroro-jobs](https://github.com/Bae-ChangHyun/changroro-jobs) |
| **newsletter** | 7개 소스 AI 뉴스 수집, 카테고리 분류, Telegram 전송 | [changroro-newsletter](https://github.com/Bae-ChangHyun/changroro-newsletter) |
| **deep-audit** | 멀티 라운드 병렬 팀 감사 — 매직넘버·silent fallback·기능 검증 | [changroro-deep-audit](https://github.com/Bae-ChangHyun/changroro-deep-audit) |

---

### docs

블로그, 일지, README, 포트폴리오를 생성한다.

<details>
<summary>상세</summary>

**Agents** — `blog-writer`(Tistory 스타일 단일 md + inline HTML, 로컬 이미지 수집) · `worklog-writer`(경영진 보고용) · `devlog-writer`(기술 상세) · `portfolio-writer`

**Skills** — `readme`(배너 + 스크린샷 + 8단 OSS skeleton) · `session-handover`(AGENTS.md + CLAUDE.md 임포트 + HANDOFF.md 관리, 오염 콘텐츠 자동 재배치) · `terminal-gif-maker`(VHS 기반 결정론적 터미널 녹화)

**Commands** — `/docs:blog` `/docs:worklog` `/docs:devlog` `/docs:portfolio` `/docs:configure`

</details>

### gitwf

<details>
<summary>상세</summary>

**Skills** — `git-commit`(Conventional Commits + Emoji) · `github-pr-creation` · `github-pr-merge` · `github-pr-review`

커밋은 파일 단위가 아니라 작업 단위로 묶는다. 한 요청 = 한 커밋이 기본값이다.

</details>

### jobs

<details>
<summary>상세</summary>

**워크플로우** — `init` → `crawl` → `research` → `write` → `review` → `interview`

| 스킬 | 하는 일 |
|---|---|
| `init` | 폴더 구조 생성 (현재 디렉토리 기준) |
| `crawl` | 채용공고 URL 크롤링 → 마크다운 정리 |
| `research` | 기업분석 + 직무분석 에이전트 병렬 실행 |
| `write` | 문항 유형 자동 판별 → 자소서 2~3개 버전 |
| `review` | 클리셰 검사, AI 티 제거, 일관성 검증 |
| `interview` | 1분 자기소개, 예상 질문 100개, 모의면접 |

모든 경로가 상대경로이고, 프롬프트 템플릿 16개가 들어 있다.

</details>

### newsletter

<details>
<summary>상세</summary>

**수집 소스** — HN, Reddit, GeekNews, TLDR, Threads, Velopers, DevDay

```bash
/newsletter:ai-news-onboard   # 최초 설정 (플랫폼, Telegram bot_token, 주기)
/newsletter:ai-news-start     # 시스템 crontab 등록
/newsletter:ai-news-stop      # 해제
/newsletter:ai-news-now       # 즉시 1회 수집
```

카테고리 자동 분류(모델&리서치·도구&오픈소스·보안·업계동향·개발실무), 점수 기반 필터링(HN/Reddit ≥ 3, GeekNews ≥ 5), 크로스소스 URL 중복 제거, Telegram MarkdownV2 하이퍼링크 전송.

시스템 cron + `claude -p` 조합이라 Claude Code 세션을 띄워둘 필요가 없다. PC만 켜져 있으면 된다.

</details>

### deep-audit

<details>
<summary>상세</summary>

코드베이스 전체를 정찰해 기능 단위 조사 계획을 세우고, 팀원 여러 명에게 기능별로 분배해 병렬 분석·실동작 테스트를 시킨다. 승인된 수정을 적용한 뒤 **이전과 겹치지 않는 새 팀원**을 소집해 같은 과정을 수렴할 때까지 반복한다.

중점 항목 — 의도하지 않은 매직넘버·하드코딩, 불필요한 주석·docstring, silent fallback·silent default, 각 기능이 기획 의도대로 실제로 동작하는지, 그리고 보안 취약점·데드코드·레거시·UI/UX.

단일 PR 리뷰나 한 파일만 보는 요청에는 과하다. 그럴 땐 전용 리뷰 도구를 쓰는 게 낫다.

</details>

---

## 데스크톱 알림 (Hooks)

| 이벤트 | 알림 | Urgency |
|---|---|---|
| 권한 요청 | 권한 승인이 필요합니다 | critical |
| 입력 대기 | 입력을 기다리고 있습니다 | normal |
| 작업 완료 | 작업이 완료되었습니다 | normal |

## 업데이트

```bash
/plugin marketplace update changroro-plugins
/plugin update docs@changroro-plugins
```

버전은 각 플러그인 저장소의 `.claude-plugin/plugin.json`이 기준이다. 마켓플레이스는 버전을 따로 적지 않는다.

## 라이선스

MIT — [LICENSE](./LICENSE)
