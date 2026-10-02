# project-rename

**Claude·Codex 세션만 옮기거나, 프로젝트 폴더와 세션 전체를 함께 이관합니다.**

[마켓플레이스](../../README.md) · [플러그인 소스](.)

## 설치

```text
/plugin marketplace add Changroro/plugins
/plugin install project-rename@changroro
```

공용 스크립트와 역할 정의가 포함되므로 전체 플러그인을 설치합니다.

## 두 가지 명령

| 명령 | 자연어 요청 | 처리 방식 |
|---|---|---|
| [mv-session](skills/mv-session/SKILL.md) | “~의 클로드 세션 옮겨줘”, “~의 코덱스 세션 옮겨줘” | 서브에이전트 없이 스크립트로 지정한 세션만 이동 |
| [mv-project](skills/mv-project/SKILL.md) | “~ 전체 프로젝트 폴더 및 세션 옮겨줘” | 에이전트가 외부 경로·링크를 조사·수정하고 스크립트가 폴더·세션을 이관 |

Claude Code는 `/project-rename:mv-session`, `/project-rename:mv-project`, Codex는 `$project-rename:mv-session`, `$project-rename:mv-project`로 호출합니다. 명령 이름과 최종 이동 결과는 두 도구에서 같습니다.

## mv-session — 세션만 이동

프로젝트 파일·다른 세션·공유 memory·공용 설정은 유지합니다. 목적지 폴더를 준비하고 이동할 도구·세션 ID를 지정합니다. 참조 조사 에이전트는 호출하지 않습니다.

Claude는 같은 ID로 세션과 부속 파일을 복사·검증한 다음 원본 세션과 인덱스의 해당 항목을 제거합니다. 원본은 복구용 백업에 보관하며 활성 세션은 목적지 하나에만 남습니다. Codex는 같은 rollout 파일을 유지하면서 선택한 세션의 경로 메타데이터·DB cwd를 재지정합니다.

Codex의 현재 대화 중인 세션이 대상이면 시작 전에 **다른 세션에서 실행하라는 안내와 함께 중단**합니다. 조사 작업자를 실행자로 삼거나 현재 ID를 바꿔 우회하지 않습니다.

```bash
PLUGIN_ROOT="/absolute/path/to/project-rename"
uv run --python 3.11 python "$PLUGIN_ROOT/scripts/codex_rename.py" mv-session \
  --session-id <대상-ID> --destination /absolute/new \
  --codex-home /actual/codex --codex-db /actual/sqlite/state_N.sqlite \
  --out /outside/destination/codex-session-backup
```

Claude도 같은 `mv-session`이며 저장 구조에 맞는 `--source`, `--session-file`, `--claude-home`을 사용합니다. 정확한 인수는 [mv-session 스킬](skills/mv-session/SKILL.md)에 있습니다.

## mv-project — 프로젝트 전체 이동

```text
모드·경로 확정 → 현재 Codex 세션 검사 → 참조 조사·변경안 → 계획·백업·승인 → 폴더·세션 이동 + 외부 참조 수정 → 검증
```

외부 참조 조사는 읽기 전용 Haiku·Luna 작업자가 담당합니다. 메인 에이전트가 상대 경로·심링크·형식별 설정의 변경을 판단하고 수정·검증합니다. 단순 절대 경로는 `--reference-map`으로 계획에 넣을 수 있습니다. 세션 JSONL·DB·인덱스·설정의 고정 변환과 실제 폴더 rename은 스크립트가 담당합니다.

두 도구를 함께 쓰면 어느 폴더도 옮기기 전에 Codex의 현재 세션 검사를 마칩니다. 첫 도구가 폴더와 자기 세션을 옮기고 두 번째 도구의 plan에는 `--sessions-only`로 나머지 세션 경로만 갱신합니다. 숨김·미커밋 파일을 유지합니다.

```bash
uv run --python 3.11 python "$PLUGIN_ROOT/scripts/codex_rename.py" mv-project plan \
  --source /absolute/old --destination /absolute/new \
  --codex-home /actual/codex --codex-db /actual/sqlite/state_N.sqlite \
  --out /outside/project/codex-project-plan
uv run --python 3.11 python "$PLUGIN_ROOT/scripts/codex_rename.py" mv-project apply \
  --plan /outside/project/codex-project-plan/plan.json --approve <계획-SHA256>
```

Claude는 같은 명령과 `scripts/claude_rename.py`·Claude 상태 홈 인수를 사용합니다. [mv-project 스킬](skills/mv-project/SKILL.md)에 도구별 절차가 있습니다. Luna 참조 조사 역할은 [codex-renamer.toml](codex/agents/codex-renamer.toml)입니다.

## 검증과 지원 범위

기존 ID·대화·도구 결과·타임스탬프를 유지합니다. 완료는 실제 검증 결과·대상 ID·변경 건수·원본 제거 또는 새 cwd에 근거합니다. 백업 사본은 복구 자료이며 활성 세션으로 등록하지 않습니다. Codex 복구는 대상 DB 행만 되돌리고 전체 DB를 덮어쓰지 않습니다.

현재 writer 검사는 Linux를 지원하며 `uv`와 Python 3.11이 필요합니다. 기록 중인 파일·DB 잠금 실패·기존 Claude 목적지·미지원 구조에서는 중단합니다. 프로젝트 rename은 파일시스템 간 이동·Git worktree를 사전 차단합니다. 프로세스 종료·재시작·서버 실행·세션 재개·검증 메시지 전송은 하지 않습니다.

ASM의 이관 방식을 참고한 독립 구현이며 ASM 설치·호출은 필요하지 않습니다. 실제 Claude 기록의 복사와 Codex 세션의 경로 재지정을 검증했고 Codex는 사용자가 재개해 확인했습니다. Claude의 복사 후 원본 제거·실패 복구는 임시 데이터로 검증합니다. Luna 호출까지 포함한 통합 검증과 macOS writer 검사 지원은 별도 검증 범위입니다.

```bash
uv run --python 3.11 python -B -m unittest discover -s tests/project_rename -v
```

## 라이선스

[MIT License](../../LICENSE).
