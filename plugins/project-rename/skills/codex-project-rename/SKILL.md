---
name: codex-project-rename
description: 프로젝트 폴더를 rename하면서 Codex의 기존 세션 ID·대화 내용을 유지하고 rollout 메타데이터·세션 DB cwd·프로젝트 등록·신뢰 설정의 경로 참조를 자동 수정한다. Claude 데이터는 수정하지 않는다.
---

# Codex Project Rename

ASM `codex_data.move_session`의 기존 ID 유지·rollout 경로 메타데이터 수정 방식을 참고한 독립 구현이다. ASM을 실행하거나 가져오지 않는다. 고정 작업은 이 플러그인의 `scripts/codex_rename.py`가 수행한다. 등록된 `codex-renamer` Luna 작업자에 조사와 스크립트 실행을 맡긴다. 정의는 플러그인 `codex/agents/codex-renamer.toml`이며, 역할이 없으면 등록 변경안을 승인받는다. 모델 지정 도구가 있으면 `gpt-6-luna`를 사용한다. 대상 세션을 작업자로 호출하거나 모델 제한을 우회하지 않는다.

1. 이전·새 절대 경로와 조사할 디렉터리를 확정한다. 실제 `CODEX_HOME`, `sqlite_home`/`CODEX_SQLITE_HOME`과 활성 상태 DB를 확인한다. 레거시 홈을 합산하거나 홈 전체·`/`를 검색하지 않는다.
2. 지정한 범위에서 경로 참조를 조사하고 일반 파일의 확인한 참조만 `--reference-map FILE OLD NEW`로 지정한다. 세션/DB는 도구 전용 변환으로 자동 처리하며 일반 문자열 전체 치환에 넣지 않는다.
3. 스크립트는 DB의 현재 cwd로 해당 프로젝트의 파일만 선택하고, 현재·보관 rollout의 `session_meta`, `turn_context`, `thread_settings_applied` 경로 메타데이터를 자동 수정한다. 하위 디렉터리 suffix를 유지하고 비슷한 이름의 다른 프로젝트를 건드리지 않는다. 세션 DB의 대상 `threads.cwd`, 글로벌 프로젝트/작업 등록 경로, `config.toml`의 프로젝트 신뢰 키도 자동 갱신한다. rollout의 날짜별 저장 위치·ID·본문·도구 입력/결과·타임스탬프는 유지한다.
4. 계획의 파일·DB 행·폴더 목록, diff와 백업 위치·SHA256을 보여주고 승인받는다. DB/rollout 소속 불일치·잘못된 JSON·미지원 DB 스키마/cwd에 영향을 주는 트리거·기존 목적지는 변경 전에 중단한다.

```bash
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py plan \
  --source /absolute/old --destination /absolute/new \
  --codex-home /actual/codex --codex-db /actual/sqlite/state_N.sqlite \
  --out /outside/project/codex-rename-plan
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py apply --plan /outside/project/codex-rename-plan/plan.json --approve <계획 SHA256>
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py verify --plan /outside/project/codex-rename-plan/plan.json
uv run --python 3.11 python <플러그인 경로>/scripts/codex_rename.py rollback --plan /outside/project/codex-rename-plan/plan.json --approve <같은 SHA256>
```

`--out`은 프로젝트·세션 저장소 밖의 새 디렉터리다. 파일의 변경 전/후 원문과 SQLite backup API의 일관된 백업을 보관하며 비밀을 응답에 노출하지 않는다. DB가 있으면 실제 활성 DB를 `--codex-db`로 명시한다. 다른 스킬이 이미 폴더를 rename했다면 plan에 `--sessions-only`를 추가해 Codex 경로만 갱신한다.

기록 중인 대상 rollout은 적용 전에 차단한다. 공유 DB의 열린 연결만으로 쓰기 중이라고 판정하지 않으며, 폴더 변경 전에 BEGIN IMMEDIATE 잠금을 얻지 못하면 아무것도 바꾸지 않고 중단한다. 프로세스 종료·재시작·신호, Codex 서버 실행·세션 API, fork/start/resume, 검증 메시지, 백그라운드 작업은 하지 않는다. 사용자가 데이터 기록을 마친 뒤 적용하며, 스크립트의 현재 Linux writer 검사를 우회하지 않는다. DB는 쓰기 잠금과 기존 cwd 비교로 다른 연결의 쓰기를 직렬화한다. 앱 상태 JSON이 동시에 변경되면 해시 검사로 중단하고 다른 변경을 덮어쓰지 않는다.

검증은 기존 ID·메시지/도구 결과 보존과 모든 계획 경로의 갱신 여부를 대조한다. DB는 대상 행의 기존 cwd를 확인한 트랜잭션으로 갱신하고 복구도 해당 행만 되돌린다. 다른 프로젝트의 행·원문·아카이브 상태는 유지한다. 전체 DB를 백업으로 덮어써 다른 작업을 지우지 않는다. 일반 rename은 숨김·미커밋 파일을 유지하고 실패하면 폴더명·수정한 경로만 복구한다. Claude 세션도 있으면 Claude용 별도 스킬까지 적용해야 전체 이관 완료다. 결과에 기존 ID 유지·대화 보존·자동 갱신 범위·남은 외부 참조·백업 위치를 보고한다.
