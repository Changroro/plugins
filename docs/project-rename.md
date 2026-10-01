# project-rename

**프로젝트 이름·경로를 바꾸면서 Claude·Codex의 기존 세션과 내부 경로 참조를 함께 이관합니다.**

[마켓플레이스](../README.md) · [플러그인 소스](../plugins/project-rename)

## 소개

폴더명만 바꾸면 세션이 이전 경로를 참조하거나 로컬 파일의 연결이 끊길 수 있습니다. Claude와 Codex의 저장 구조에 맞는 별도 스킬로 계획·백업·적용·검증·복구를 수행합니다. ASM의 이관 방식을 참고한 독립 구현이며 ASM 설치나 호출은 필요하지 않습니다.

## 설치와 첫 사용

Claude Code에서 전체 플러그인을 설치합니다. 스킬 폴더만 복사하면 공용 스크립트가 누락됩니다.

```text
/plugin marketplace add Changroro/plugins
/plugin install project-rename@changroro
/project-rename:claude-project-rename
/absolute/old를 /absolute/new로 바꿔줘. 참조 조사는 /absolute/related 안에서 해줘.
```

Codex는 설치한 `$project-rename:codex-project-rename` 스킬을 호출합니다. Claude 작업자는 Haiku이며 Codex는 [codex-renamer 정의](../plugins/project-rename/codex/agents/codex-renamer.toml)를 등록한 Luna 작업자를 사용합니다. 역할이 없으면 등록 변경안을 먼저 제시합니다.

## 두 도구의 처리 범위

| 스킬 | 자동 갱신하는 데이터 |
|---|---|
| [claude-project-rename](../plugins/project-rename/skills/claude-project-rename/SKILL.md) | 인코딩된 세션 디렉터리, JSONL 경로 메타데이터, 인덱스, 프로젝트 설정·연관 데이터 |
| [codex-project-rename](../plugins/project-rename/skills/codex-project-rename/SKILL.md) | 현재·보관 rollout 경로 메타데이터, 대상 DB 행의 `cwd`, 프로젝트 등록, TOML 신뢰 설정 |

일반 파일 참조는 지정한 디렉터리에서 조사하고 확인한 파일·이전 값·새 값을 `--reference-map`으로 계획에 추가합니다. 홈 전체를 검색하거나 메시지 본문을 일괄 치환하지 않습니다.

기존 ID·대화 본문·도구 입력과 결과·타임스탬프를 유지합니다. Codex DB는 대상 프로젝트 행만 갱신하고 복구도 그 행만 되돌립니다.

## 작동 방식

```text
경로·조사 범위 확정 → 계획·백업·diff → 계획 해시 승인 → rename·참조 수정 → 검증
```

폴더는 실제 rename으로 이동합니다. 목적지가 이미 존재하거나 지원하지 않는 저장 구조·쓰기 상태가 발견되면 적용 전에 중단합니다. 숨김·미커밋 파일은 폴더와 함께 유지됩니다.

두 도구를 함께 쓴 프로젝트는 첫 스킬로 폴더와 해당 도구 경로를 변경하고, 두 번째 스킬에서 `--sessions-only`로 나머지 도구의 세션 경로를 수정합니다.

## 스크립트 사용

아래는 Codex 계획 생성 예시입니다. 설치된 플러그인 절대 경로와 실제 상태 홈·DB를 확인해 값을 바꿉니다.

```bash
PLUGIN_ROOT="/absolute/path/to/project-rename"
uv run --python 3.11 python "$PLUGIN_ROOT/scripts/codex_rename.py" plan \
  --source /absolute/old --destination /absolute/new \
  --codex-home /actual/codex --codex-db /actual/sqlite/state_N.sqlite \
  --out /outside/project/codex-rename-plan
```

`apply`, `verify`, `rollback` 인수는 [Codex 스킬](../plugins/project-rename/skills/codex-project-rename/SKILL.md)에 있습니다. Claude는 [별도 스크립트·상태 홈 인수](../plugins/project-rename/skills/claude-project-rename/SKILL.md)를 사용합니다. 백업 위치는 프로젝트·세션 저장소 밖의 새 디렉터리로 지정합니다.

## 안전성·지원 범위와 검증

현재 적용 전 writer 검사는 Linux를 지원하며 실행에는 `uv`와 Python 3.11이 필요합니다. 파일시스템 간 이동·Git worktree 등 지원하지 않는 조건은 사전 검사에서 차단합니다. 기록 중인 대상 파일을 검사하고 Codex DB 쓰기 잠금을 폴더 변경 전에 확보합니다.

프로세스를 종료·재시작하거나 Codex 서버를 실행하지 않습니다. 세션 분기·시작·재개 또는 검증 메시지 전송도 하지 않습니다. 기록 중이면 사용자가 기록을 마친 후 적용합니다.

저장소 루트에서 회귀 테스트를 실행합니다.

```bash
uv run --python 3.11 python -B -m unittest discover -s tests/project_rename -v
```

Claude는 임시 데이터로 검증했고 Codex는 로컬 시험 프로젝트의 실제 기록에서 경로 갱신과 기존 ID·대화 원문 보존을 확인했습니다. 실제 Claude 데이터 검증과 macOS writer 검사 지원은 추가 검증이 필요한 범위입니다.

## 라이선스

[MIT License](../LICENSE).
