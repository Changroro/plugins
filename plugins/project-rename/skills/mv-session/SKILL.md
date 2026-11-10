---
name: mv-session
description: 사용자가 특정 프로젝트의 클로드 세션 또는 코덱스 세션을 다른 폴더로 옮겨 달라고 할 때 사용한다. 프로젝트 파일은 유지하고 지정한 기존 세션만 asm move로 이동한다. 세션 ID는 유지되고 원본은 목적지 하나에만 남는다.
---

# Move Session

“~의 클로드 세션 옮겨줘”, “~의 코덱스 세션 옮겨줘”는 이 스킬이다. 복사(원본 유지, 새 ID)는 `cp-session`, 프로젝트 폴더째 이동은 `mv-project`다. 실제 작업은 asm(`agent-session-manager`)이 하고, 에이전트는 대상을 확정하고 결과를 전달한다. 세션 JSONL·Codex DB·설정을 직접 편집하지 않는다.

## 준비

`asm move --help`가 실패하면 **“asm 0.16.1 이상이 필요합니다: `uv tool install --upgrade agent-session-manager`”**라고 안내하고 중단한다. 다른 방법으로 우회하지 않는다.

원본 프로젝트 경로·목적지 경로·대상 세션을 확정한다. 세션이 모호하면 `asm find <검색어>`나 `asm find --project <원본 경로>`로 후보를 보여 주고 사용자에게 고르게 한다. 목록의 짧은 ID(8자리 이상)를 그대로 쓴다.

## 실행

```bash
asm move /absolute/old /absolute/new --sessions <ID> [<ID> ...] --yes --json
```

`--sessions`를 빼면 원본 경로의 Claude·Codex 세션 전부를 옮기므로, 사용자가 “전부”라고 한 경우에만 뺀다. `--yes`는 사용자가 이동 대상을 확인한 뒤에만 붙인다.

asm이 처리하는 것: Claude는 세션 파일과 `<ID>/` 하위 폴더(서브에이전트·도구 결과)를 옮기고 경로를 새 위치로 바꾸며, 원본은 복구 스냅샷과 함께 휴지통으로 보낸다. Codex는 rollout 메타데이터와 `state_N.sqlite`의 cwd를 함께 바꾼다. 목적지에 같은 ID가 있으면 건너뛴다.

## 중단·완료

asm이 “session in use by a running Claude Code/Codex”로 거부하면 그대로 전달한다. 현재 대화 중인 세션이면 **“현재 대화 중인 세션은 이관할 수 없습니다. 다른 세션에서 이 명령을 실행하세요.”**라고 안내한다. 프로세스를 끄거나 ID를 바꿔 우회하지 않는다.

JSON 결과의 `success`, Claude `moved`·`skipped`, Codex `moved`·`failed`를 보고한다. 실패가 있으면 그 메시지를 그대로 전달한다. 되돌리기는 `asm recovery list` → `asm recovery restore <id>`다. 이동한 세션을 실행해 검증하지 않는다.
