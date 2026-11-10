# project-rename

**Claude·Codex 세션을 옮기거나 복사하고, 프로젝트 폴더를 세션째 이전합니다.** 실제 작업은 [asm(agent-session-manager)](https://github.com/Changroro/agent-session-manager)이 하고, 이 플러그인은 에이전트가 asm을 올바르게 호출하도록 안내합니다.

[마켓플레이스](../../README.md) · [플러그인 소스](.)

## 설치

```text
/plugin marketplace add Changroro/plugins
/plugin install project-rename@changroro
uv tool install --upgrade agent-session-manager   # asm 0.16.1 이상
```

asm이 없거나 오래되면 스킬은 설치 안내를 하고 멈춥니다.

## 세 가지 명령

| 명령 | 자연어 요청 | asm 호출 |
|---|---|---|
| [mv-session](skills/mv-session/SKILL.md) | “~의 클로드/코덱스 세션 옮겨줘” | `asm move <원래> <새> --sessions <ID>` — ID 유지, 원본은 복구 스냅샷과 함께 휴지통 |
| [cp-session](skills/cp-session/SKILL.md) | “~ 세션 복사해줘” | `asm copy <원래> <새> --sessions <ID>` — 원본 유지, 새 ID |
| [mv-project](skills/mv-project/SKILL.md) | “~ 전체 프로젝트 폴더 및 세션 옮겨줘” | `asm relocate <원래> <새>` + 남은 경로 참조는 에이전트가 조사·수정 |

Claude Code는 `/project-rename:<명령>`, Codex는 `$project-rename:<명령>`으로 호출합니다.

## AI가 하는 일과 asm이 하는 일

asm은 정해진 규칙대로만 처리합니다: 폴더 rename, 세션 파일과 서브에이전트·도구 결과 폴더, Codex rollout과 `state_N.sqlite`, `~/.claude.json`·Codex `config.toml`의 프로젝트 키, `git worktree repair`. 새 폴더 안에서 옛 경로가 남은 파일은 고치지 않고 목록으로만 돌려줍니다.

에이전트는 그 목록(과 사용자가 지정한 범위)만 조사해 파일별 변경안을 승인받고 수정합니다. 조사는 읽기 전용 작업자가 맡습니다: Claude [claude-renamer](agents/claude-renamer.md)(Haiku), Codex [codex-renamer](codex/agents/codex-renamer.toml)(Luna).

## 안전장치

실행 중인 Claude Code·Codex가 쓰고 있는 세션(현재 대화 포함)이나, Claude Code가 작업 중인 폴더는 asm이 거부합니다. 이동·삭제하는 원본은 `~/.asm/recovery` 스냅샷이 남아 `asm recovery restore <id>`로 되돌릴 수 있습니다. 다른 파일시스템으로의 폴더 이전은 지원하지 않습니다.

## 라이선스

[MIT License](../../LICENSE).
