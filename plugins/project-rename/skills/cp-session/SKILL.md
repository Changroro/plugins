---
name: cp-session
description: 사용자가 클로드 또는 코덱스 세션을 다른 폴더로 복사해 달라고 할 때 사용한다. 원본은 그대로 두고 asm copy로 새 세션 ID의 복사본을 만든다.
---

# Copy Session

“~의 세션 복사해줘”, “이 세션을 다른 폴더에서도 이어 쓰고 싶어”는 이 스킬이다. 원본을 옮기는 요청은 `mv-session`이다. 실제 작업은 asm(`agent-session-manager`)이 한다.

## 준비

`asm copy --help`가 실패하면 **“asm 0.16.1 이상이 필요합니다: `uv tool install --upgrade agent-session-manager`”**라고 안내하고 중단한다.

원본 프로젝트 경로·목적지 경로·대상 세션을 확정한다. 모호하면 `asm find <검색어>` 결과에서 사용자가 고르게 한다.

## 실행

```bash
asm copy /absolute/old /absolute/new --sessions <ID> [<ID> ...] --yes --json
```

`--sessions`를 빼면 원본 경로의 세션 전부를 복사하므로 “전부”라고 한 경우에만 뺀다. 복사본은 새 세션 ID를 받는다. Claude는 파일명·`sessionId`·하위 폴더명이 새 ID로 바뀌고, Codex는 새 rollout과 `state_N.sqlite` 행이 생기며 토큰 사용량은 0으로 기록돼 비용이 두 번 집계되지 않는다. 원본은 바뀌지 않는다.

## 완료

JSON 결과의 `ids`(원본 ID → 새 ID)를 그대로 보고하고, 이어 열 때 쓸 명령을 함께 알려 준다: Claude `cd /absolute/new && claude -r <새 ID>`, Codex `cd /absolute/new && codex resume <새 ID>`.
