---
name: mv-session
description: 사용자가 특정 프로젝트의 클로드 세션 또는 코덱스 세션을 다른 폴더로 옮겨 달라고 할 때 사용한다. 프로젝트 파일은 유지하고 지정한 기존 세션만 이동한다. Claude·Codex 모두 최종 세션은 목적지 하나에만 남는다.
---

# Move Session

“~의 클로드 세션 옮겨줘”, “~의 코덱스 세션 옮겨줘”는 이 스킬이다. 프로젝트 폴더·파일 전체 이동은 `mv-project`로 처리한다. 도구·대상 ID·목적지가 모호하면 확인한다. 서브에이전트를 호출하거나 외부 참조 파일을 조사·수정하지 않는다. 세션 이동·백업·검증은 스크립트가 처리한다.

## 시작 전

실제 Claude/Codex 상태 홈과 대상 ID·원본 소속을 확인하고 목적지 폴더를 준비한다. 백업은 상태 홈·목적지 밖의 새 디렉터리에 둔다. Codex는 실제 활성 DB와 현재 실행 세션 ID를 확인한다. 대상이 현재 대화 중인 세션이면 **“현재 대화 중인 Codex 세션은 이관할 수 없습니다. 다른 세션에서 이 명령을 실행하세요.”**라고 안내하고 중단한다. 에이전트를 대신 실행시켜 우회하지 않는다. 스크립트도 백업·수정 전에 검사하며 `CODEX_THREAD_ID`를 바꾸지 않는다. 환경에 ID가 없을 때만 실제 현재 ID를 `--caller-thread-id`로 전달한다.

## 실행

사용자 명령은 두 도구 모두 `mv-session`이다. 메인 에이전트는 요청된 도구에 해당하는 아래 스크립트를 실행하고 결과를 전달한다.

Claude는 선택한 세션을 같은 ID로 복사하고 검증한 뒤 원본 세션·부속 파일·원본 인덱스의 해당 항목을 제거한다. 원본 데이터는 상태 홈 밖의 백업에 보관하며 프로젝트 파일·다른 세션·공유 memory·전역 설정은 유지한다.

```bash
uv run --python 3.11 python <플러그인 경로>/scripts/claude_rename.py mv-session \
  --source /absolute/old --destination /absolute/new \
  --session-file /actual/claude/projects/<encoded-old>/<existing-id>.jsonl \
  --claude-home /actual/claude --out /outside/destination/claude-session-backup
```

Codex는 DB에서 선택한 ID의 실제 cwd를 읽고 그 세션의 rollout 경로 메타데이터·DB cwd를 재지정한다. 같은 날짜별 rollout 파일을 유지하며 폴더·다른 세션·공용 설정을 바꾸지 않는다. 홈에서 시작한 세션도 ID로 선택하고 홈 폴더는 옮기지 않는다.

```bash
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py mv-session \
  --session-id <대상 ID> --destination /absolute/new \
  --codex-home /actual/codex --codex-db /actual/sqlite/state_N.sqlite \
  --out /outside/destination/codex-session-backup
```

## 완료 조건

기존 ID·대화 본문·도구 입력/결과·UUID·타임스탬프를 유지한다. Claude는 audit.json의 verified·source_removed와 목적지 해시·원본 세션 부재를, Codex는 state.json의 applied와 verified 결과·대상 ID·DB/rollout cwd를 확인한다. 목적지의 기존 대화를 실행해 검증하지 않는다. 백업 사본은 복구용이며 활성 세션 중복으로 취급하지 않는다.

없는 ID·현재 Codex 세션·잘못된 형식·기존 Claude 목적지·기록 중인 파일·권한 부족·DB 잠금 실패는 중단한다. 현재 writer 검사는 Linux를 지원하며 우회하지 않는다. 프로세스 종료·재시작·신호, Codex 서버 실행, 세션 분기·시작·재개, 검증 메시지·백그라운드 작업은 하지 않는다. 결과에는 실제 대상 ID·목적지·검증 여부·백업 위치만 보고한다.
