# cc-plugins-bch

개인용 Claude Code 플러그인 마켓플레이스입니다.

## Installation

```bash
# 마켓플레이스 추가
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch

# 플러그인 설치
/plugin install dev_ch@cc-plugins-bch
```

## Plugins

### dev_ch

커스텀 에이전트, 스킬, MCP 서버를 포함한 개인용 Claude Code 플러그인입니다.

---

## Agents

에이전트는 Task 도구를 통해 자동으로 호출되거나, 슬래시 커맨드로 직접 실행할 수 있습니다.

| Agent | Description | 주요 기능 |
|-------|-------------|-----------|
| `dev_ch:blog-writer` | 기술 블로그 글 작성 | URL 참조, 마크다운/HTML 출력 |
| `dev_ch:daily-work-writer` | 업무일지 생성 (보고용) | git 커밋 분석, 경영진 보고 형식 |
| `dev_ch:daily-work-details-writer` | 상세 개발일지 생성 | git 커밋 분석, 기술적 세부사항 기록 |
| `dev_ch:portfolio-writer` | 포트폴리오 작성/업데이트 | 프로젝트 분석, 기술 스택 정리 |
| `dev_ch:product-advisor` | 프로젝트 전략 분석 | 개선점 제안, 기능 추천 |
| `dev_ch:readme-architect` | README.md 작성/개선 | 오픈소스 베스트 프랙티스 적용 |
| `dev_ch:senior-code-reviewer` | 종합 코드 리뷰 | 아키텍처, 기능, 비즈니스 관점 |
| `dev_ch:stack-updater` | 기술 스택 최신화 | 최신 문서 조회, 베스트 프랙티스 적용 |

---

## Commands (Slash Commands)

### 문서 생성

| Command | Description | Arguments |
|---------|-------------|-----------|
| `/dev_ch:docs` | **문서 일괄 생성** | `--path <경로>` `--since <날짜>` `--skip-confirm` |
| `/dev_ch:portfolio` | 포트폴리오 작성 | 프로젝트 경로 (선택) |
| `/dev_ch:worklog` | 업무일지 생성 | 날짜 범위, 출력 경로 (선택) |
| `/dev_ch:devlog` | 상세 개발일지 생성 | 날짜 범위, 출력 경로 (선택) |
| `/dev_ch:readme` | README 작성/개선 | 프로젝트 정보 (선택) |
| `/dev_ch:blog` | 기술 블로그 글 작성 | `<주제> <참고URL> <format> [출력경로]` |

#### `/dev_ch:docs` 상세

문서를 일괄 생성합니다. 실행 시 다음을 인터랙티브하게 확인합니다:
- 문서를 작성할 프로젝트 경로
- 분석할 커밋 날짜 범위
- 생성할 문서 종류 선택 (portfolio, worklog, devlog)

```bash
# 기본 실행 (인터랙티브)
/dev_ch:docs

# 옵션 지정
/dev_ch:docs --path /home/user/project --since 2024-01-01

# 확인 없이 바로 실행
/dev_ch:docs --skip-confirm
```

#### `/dev_ch:blog` 상세

```bash
# 마크다운 형식
/dev_ch:blog MCP 프로토콜 https://modelcontextprotocol.io markdown

# HTML 형식 + 커스텀 경로
/dev_ch:blog FastAPI 시작하기 https://fastapi.tiangolo.com html /home/user/blog/
```

### 코드 리뷰 & 분석

| Command | Description | Arguments |
|---------|-------------|-----------|
| `/dev_ch:review` | 종합 코드 리뷰 | 리뷰 대상 파일/범위 (선택) |
| `/dev_ch:advisor` | 프로덕트 어드바이저 | 분석할 기능/영역 (선택) |
| `/dev_ch:update-stack` | 기술 스택 업데이트 | 업데이트할 기술명 (선택) |

### 설정

| Command | Description | Arguments |
|---------|-------------|-----------|
| `/dev_ch:help` | 사용 가능한 모든 명령어 목록 | - |
| `/dev_ch:config` | 현재 설정 확인 | - |
| `/dev_ch:config-set` | 설정 값 변경 | `<key> <value>` |

```bash
# 설정 확인
/dev_ch:config

# 설정 변경
/dev_ch:config-set blog_path "공부/기술블로그"
```

---

## Skills

| Skill | Description | 자동 적용 |
|-------|-------------|-----------|
| `/dev_ch:commit` | Git 커밋 베스트 프랙티스 | 커밋 생성 시 자동 적용 |

커밋 스킬은 다음 원칙을 적용합니다:
- **기능 단위 커밋**: 관련 파일을 하나의 커밋으로 묶음
- **결과 중심 메시지**: 과정이 아닌 최종 변경점만 기술

---

## MCP Servers

| Server | Description | Link |
|--------|-------------|------|
| **playwright** | 브라우저 자동화 및 웹 페이지 조작 | [GitHub](https://github.com/microsoft/playwright-mcp) |
| **context7** | 라이브러리/프레임워크 최신 문서 조회 | [GitHub](https://github.com/upstash/context7) |
| **mcp-obsidian** | Obsidian 볼트 연동 (노트 읽기/쓰기) | [GitHub](https://github.com/smithery-ai/mcp-obsidian) |

---

## Configuration

### 환경변수 설정

```bash
export OBSIDIAN_API_KEY="your-obsidian-api-key"
```

### config.json

설치 후 `~/.claude/plugins/cache/.../dev_ch/config.json`에서 경로를 환경에 맞게 수정하세요:

```json
{
  "obsidian_base": "/your/obsidian/vault/path",
  "worklog_path": "docs/daily_work",
  "devlog_path": "docs/daily_work_details",
  "portfolio_path": "docs/portfolio",
  "blog_path": "공부/알쓸신잡"
}
```

| Key | Description | Default |
|-----|-------------|---------|
| `obsidian_base` | Obsidian 볼트 절대 경로 | `/home/bch/obsidian_sync` |
| `worklog_path` | 업무일지 저장 경로 (상대) | `docs/daily_work` |
| `devlog_path` | 개발일지 저장 경로 (상대) | `docs/daily_work_details` |
| `portfolio_path` | 포트폴리오 저장 경로 (상대) | `docs/portfolio` |
| `blog_path` | 블로그 저장 경로 (상대) | `공부/알쓸신잡` |

---

## Update

```bash
# 마켓플레이스 동기화
/plugin marketplace update

# 플러그인 업데이트
/plugin update dev_ch@cc-plugins-bch
```

---

## Examples

### 프로젝트 문서 일괄 생성

```bash
/dev_ch:docs
# → 경로, 날짜 범위, 문서 종류를 인터랙티브하게 선택
```

### 코드 리뷰 요청

```bash
/dev_ch:review
# → 현재 프로젝트의 최근 변경사항 리뷰

/dev_ch:review src/auth 모듈 보안 점검
# → 특정 영역 집중 리뷰
```

### 블로그 글 작성

```bash
/dev_ch:blog "Claude Code 플러그인 개발" https://docs.anthropic.com markdown
```

### Git 커밋 (스킬 자동 적용)

```bash
커밋해줘
# → dev_ch:commit 스킬이 자동 적용되어 기능 단위 커밋 생성
```
