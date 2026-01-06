# cc-plugins-bch

개인용 Claude Code 플러그인 마켓플레이스입니다.

## Installation

```bash
# 마켓플레이스 추가
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch

# 플러그인 설치 (개별 또는 전체)
/plugin install docs@cc-plugins-bch    # 문서 작성
/plugin install dev@cc-plugins-bch     # 개발 지원
```

---

# docs 플러그인

문서 작성 관련 에이전트와 커맨드를 제공합니다.

## Agents

| Agent | Description | 주요 기능 |
|-------|-------------|-----------|
| `docs:blog-writer` | 기술 블로그 글 작성 | URL 참조, 마크다운/HTML 출력 |
| `docs:daily-work-writer` | 업무일지 생성 (보고용) | git 커밋 분석, 경영진 보고 형식 |
| `docs:daily-work-details-writer` | 상세 개발일지 생성 | git 커밋 분석, 기술적 세부사항 기록 |
| `docs:portfolio-writer` | 포트폴리오 작성/업데이트 | 프로젝트 분석, 기술 스택 정리 |
| `docs:readme-architect` | README.md 작성/개선 | 오픈소스 베스트 프랙티스 적용 |

## Commands

### 문서 일괄 생성

| Command | Description | Arguments |
|---------|-------------|-----------|
| `/docs:docs` | **문서 일괄 생성** | `--path <경로>` `--since <날짜>` `--skip-confirm` |

```bash
# 인터랙티브 모드 (경로, 날짜 범위, 문서 종류 선택)
/docs:docs

# 옵션 지정
/docs:docs --path /home/user/project --since 2024-01-01
```

### 개별 문서 생성

| Command | Description | Arguments |
|---------|-------------|-----------|
| `/docs:blog` | 기술 블로그 글 작성 | `<주제> <참고URL> <format> [출력경로]` |
| `/docs:worklog` | 업무일지 생성 | 날짜 범위, 출력 경로 (선택) |
| `/docs:devlog` | 상세 개발일지 생성 | 날짜 범위, 출력 경로 (선택) |
| `/docs:portfolio` | 포트폴리오 작성 | 프로젝트 경로 (선택) |
| `/docs:readme` | README 작성/개선 | 프로젝트 정보 (선택) |

```bash
# 블로그 글 작성
/docs:blog "MCP 프로토콜" https://modelcontextprotocol.io markdown

# HTML 형식 + 커스텀 경로
/docs:blog "FastAPI 시작하기" https://fastapi.tiangolo.com html /home/user/blog/
```

## MCP Servers

| Server | Description | Link |
|--------|-------------|------|
| **playwright** | 브라우저 자동화 및 웹 페이지 조작 | [GitHub](https://github.com/microsoft/playwright-mcp) |
| **context7** | 라이브러리/프레임워크 최신 문서 조회 | [GitHub](https://github.com/upstash/context7) |
| **mcp-obsidian** | Obsidian 볼트 연동 (노트 읽기/쓰기) | [GitHub](https://github.com/smithery-ai/mcp-obsidian) |

## Configuration

### 환경변수

```bash
export OBSIDIAN_API_KEY="your-obsidian-api-key"
```

### config.json

```json
{
  "obsidian_base": "/your/obsidian/vault/path",
  "worklog_path": "docs/daily_work",
  "devlog_path": "docs/daily_work_details",
  "portfolio_path": "docs/portfolio",
  "blog_path": "공부/알쓸신잡"
}
```

---

# dev 플러그인

개발 지원 관련 에이전트, 커맨드, 스킬을 제공합니다.

## Agents

| Agent | Description | 주요 기능 |
|-------|-------------|-----------|
| `dev:product-advisor` | 프로젝트 전략 분석 | 개선점 제안, 기능 추천 |
| `dev:stack-updater` | 기술 스택 최신화 | 최신 문서 조회, 베스트 프랙티스 적용 |
| `dev:senior-code-reviewer` | 종합 코드 리뷰 | 아키텍처, 기능, 비즈니스 관점 |

## Commands

| Command | Description | Arguments |
|---------|-------------|-----------|
| `/dev:review` | 종합 코드 리뷰 | 리뷰 대상 파일/범위 (선택) |
| `/dev:advisor` | 프로덕트 어드바이저 | 분석할 기능/영역 (선택) |
| `/dev:update-stack` | 기술 스택 업데이트 | 업데이트할 기술명 (선택) |

```bash
# 코드 리뷰
/dev:review
/dev:review src/auth 모듈 보안 점검

# 프로덕트 분석
/dev:advisor 현재 MVP 기능 검토

# 기술 스택 업데이트
/dev:update-stack FastAPI
```

## Skills

| Skill | Description | 자동 적용 |
|-------|-------------|-----------|
| `/dev:commit` | Git 커밋 베스트 프랙티스 | 커밋 생성 시 자동 적용 |

커밋 스킬은 다음 원칙을 적용합니다:
- **기능 단위 커밋**: 관련 파일을 하나의 커밋으로 묶음
- **결과 중심 메시지**: 과정이 아닌 최종 변경점만 기술

## MCP Servers

| Server | Description | Link |
|--------|-------------|------|
| **playwright** | 브라우저 자동화 및 웹 페이지 조작 | [GitHub](https://github.com/microsoft/playwright-mcp) |
| **context7** | 라이브러리/프레임워크 최신 문서 조회 | [GitHub](https://github.com/upstash/context7) |

---

# Update

```bash
# 마켓플레이스 동기화
/plugin marketplace update

# 플러그인 업데이트
/plugin update docs@cc-plugins-bch
/plugin update dev@cc-plugins-bch
```

---

# Examples

### 프로젝트 문서 일괄 생성

```bash
/docs:docs
# → 경로, 날짜 범위, 문서 종류를 인터랙티브하게 선택
```

### 코드 리뷰 후 커밋

```bash
/dev:review
# → 코드 리뷰 결과 확인

커밋해줘
# → dev:commit 스킬이 자동 적용되어 기능 단위 커밋 생성
```

### 블로그 글 작성

```bash
/docs:blog "Claude Code 플러그인 개발" https://docs.anthropic.com markdown
```
