---
name: mv-project
description: 사용자가 전체 프로젝트 폴더 및 Claude·Codex 세션을 함께 옮겨 달라고 할 때 사용한다. 에이전트가 외부 경로·링크 참조를 조사·수정하고 스크립트가 폴더와 해당 도구들의 기존 세션을 이관·검증한다.
---

# Move Project

“~ 전체 프로젝트 폴더 및 세션 옮겨줘”는 이 스킬이다. 세션만 이동하는 요청은 `mv-session`이며 프로젝트 참조 조사 작업자를 호출하지 않는다. ASM 방식에 기반한 독립 스크립트를 사용하며 ASM은 실행하거나 가져오지 않는다.

## 계획

1. 이전·새 절대 경로, 참조 조사 범위와 사용한 Claude·Codex 도구를 확정한다. 실제 상태 홈·설정·Codex 활성 DB를 확인한다. 홈 전체·`/`를 검색하지 않는다.
2. 폴더 이동 전에 Codex 대상 ID에 현재 실행 세션이 포함되는지 확인한다. 포함되면 **“현재 대화 중인 Codex 세션은 이관할 수 없습니다. 다른 세션에서 이 명령을 실행하세요.”**라고 안내하고 전체 이관을 중단한다. Claude를 먼저 이동하거나 작업자에게 실행을 넘겨 우회하지 않는다. `CODEX_THREAD_ID`를 바꾸지 않는다.
3. Claude 참조 조사는 Haiku(`project-rename:claude-renamer`, 또는 `general-purpose`의 `model: haiku`), Codex 참조 조사는 `codex-renamer` Luna에 맡긴다. 작업자는 지정된 일반 파일의 경로·링크 참조만 읽기 전용으로 조사해 근거와 변경 후보를 반환한다. Luna 역할 정의는 `codex/agents/codex-renamer.toml`이며 없으면 등록 변경안을 제시한다.
4. 메인 에이전트가 참조 변경을 판단한다. 단순 절대 경로는 계획에 `--reference-map FILE OLD NEW`로 넣고, 상대 경로·심링크·형식별 설정은 파일별 변경안과 백업을 준비한다. 세션 JSONL·DB·공유 상태는 직접 편집하지 않는다.
5. 스크립트로 계획·diff·백업·해시를 생성하고 전체 변경 범위를 승인받는다. 적용은 메인 에이전트가 스크립트로 실행한다. 필요한 상태 홈 접근 권한이 없으면 중단하며 작업자가 권한을 우회해 대신 실행하지 않는다.

## 이동

사용자 명령은 두 도구 모두 `mv-project`다. 스크립트가 실제 폴더 rename과 세션·인덱스·설정·DB의 고정 경로 변환을 수행하고, 에이전트가 승인한 형식별 외부 경로·링크를 수정·검증한다. 숨김·미커밋 파일, 기존 세션 ID·본문·도구 입력/결과·타임스탬프를 유지한다.

```bash
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py mv-project plan \
  --source /absolute/old --destination /absolute/new \
  --codex-home /actual/codex --codex-db /actual/sqlite/state_N.sqlite \
  --out /outside/project/codex-project-plan
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py mv-project apply --plan /outside/project/codex-project-plan/plan.json --approve <계획 SHA256>
```

Claude는 같은 `mv-project plan/apply/verify/rollback` 명령에 `scripts/claude_rename.py`와 `--claude-home /actual/claude --claude-config /actual/claude.json`을 사용한다. 설정 JSON이 없음을 확인한 경우에만 config 인수를 생략한다. 두 도구를 함께 쓰면 첫 도구가 폴더와 자기 세션을 옮기고, 두 번째 도구의 plan에는 `--sessions-only`로 나머지 세션 경로만 갱신한다. 공용 cwd에서 시작한 Codex 세션을 명시적으로 선택해야 하면 후속 계획에 `--session-id ID`를 지정한다.

## 검증·복구

```bash
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py mv-project verify --plan <백업 디렉터리>/plan.json
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py mv-project rollback --plan <백업 디렉터리>/plan.json --approve <계획 SHA256>
```

state.json의 applied와 verified 결과·실제 대상 ID·변경 건수·폴더와 세션 경로·외부 참조를 확인한 뒤 완료를 보고한다. 계획만 생성했거나 한 도구만 이관한 상태를 전체 완료로 보고하지 않는다. DB 복구는 대상 행만 되돌리며 전체 DB를 덮어쓰지 않는다. 수동 외부 참조는 백업·현재 변경을 확인해 별도로 복구한다.

현재 Linux writer 검사와 DB BEGIN IMMEDIATE 잠금을 사용한다. 기록 중인 데이터·기존 목적지·인코딩 충돌·미지원 Git worktree·파일시스템 간 rename·잘못된 구조는 중단한다. 프로세스 종료·재시작·신호, Codex 서버 실행, 세션 분기·시작·재개·검증 메시지·백그라운드 작업은 하지 않는다. 다른 작업의 변경을 덮어쓰거나 권한 검사를 우회하지 않는다.
