# cc-plugins-bch

개인용 Claude Code 플러그인 마켓플레이스입니다.

## Installation

```bash
# 마켓플레이스 추가
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch

# 플러그인 설치
/plugin install bch@cc-plugins-bch
```

## Plugins

### bch

커스텀 에이전트, 스킬, MCP 서버를 포함한 개인용 Claude Code 플러그인입니다.

#### Agents

| Agent | Description |
|-------|-------------|
| `bch:blog-writer` | 기술 블로그 글 작성 |
| `bch:daily-work-writer` | 업무일지 생성 (보고용) |
| `bch:daily-work-details-writer` | 상세 개발일지 생성 (개인 기록용) |
| `bch:portfolio-writer` | 프로젝트 포트폴리오 작성/업데이트 |
| `bch:product-advisor` | 프로젝트 전략 분석 및 개선점 제안 |
| `bch:readme-architect` | README.md 작성/개선 |
| `bch:senior-code-reviewer` | 종합 코드 리뷰 (아키텍처, 기능, 비즈니스 관점) |
| `bch:stack-updater` | 기술 스택 최신화 및 베스트 프랙티스 적용 |

#### Commands (Slash Commands)

| Command | Description |
|---------|-------------|
| `/bch:help` | 사용 가능한 모든 명령어 목록 표시 |
| `/bch:config` | 현재 설정 확인 |
| `/bch:config-set` | 설정 값 변경 |
| `/bch:review` | 코드 리뷰 에이전트 실행 |
| `/bch:portfolio` | 포트폴리오 작성 에이전트 실행 |
| `/bch:readme` | README 작성 에이전트 실행 |
| `/bch:worklog` | 업무일지 생성 |
| `/bch:devlog` | 상세 개발일지 생성 |
| `/bch:advisor` | 프로덕트 어드바이저 에이전트 실행 |
| `/bch:update-stack` | 기술 스택 업데이트 에이전트 실행 |
| `/bch:blog` | 기술 블로그 글 작성 |

#### Skills

| Skill | Description |
|-------|-------------|
| `/bch:commit` | Git 커밋 베스트 프랙티스 적용 (기능 단위 커밋, 결과 중심 메시지) |

#### MCP Servers

- **playwright**: 브라우저 자동화 및 웹 페이지 조작
- **context7**: 라이브러리/프레임워크 최신 문서 조회
- **mcp-obsidian**: Obsidian 볼트 연동 (노트 읽기/쓰기)

## Configuration

사용 전 환경변수를 설정해야 합니다:

```bash
export OBSIDIAN_BASE="/path/to/obsidian/vault"
export OBSIDIAN_API_KEY="your-api-key"
```

설치 후 `plugins/bch/config.json`에서 경로를 서버 환경에 맞게 수정하세요:

```json
{
  "obsidian_base": "/your/obsidian/path",
  "worklog_path": "docs/daily_work",
  "devlog_path": "docs/daily_work_details",
  "portfolio_path": "docs/portfolio",
  "blog_path": "your/blog/folder"
}
```

## Update

플러그인 업데이트 시:

```bash
# 마켓플레이스 동기화
/plugin marketplace update

# 플러그인 업데이트
/plugin update bch@cc-plugins-bch
```
