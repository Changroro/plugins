---
name: claude-project-rename
description: 프로젝트 폴더를 rename하면서 Claude Code의 기존 세션 ID·대화 내용을 유지하고 세션 디렉터리·인덱스·설정·내부 경로 참조를 자동 수정한다. Codex 데이터는 수정하지 않는다.
---

# Claude Project Rename

ASM `migrate.py`의 세션 ID 유지·경로 필드 수정 방식을 참고한 독립 구현이다. ASM을 실행하거나 가져오지 않는다. 고정 작업은 이 플러그인의 `scripts/claude_rename.py`가 수행한다. Haiku 작업자(`project-rename:claude-renamer` 또는 `general-purpose`의 `model: haiku`)에게 조사와 스크립트 실행을 맡긴다. 대상 세션을 작업자로 호출하지 않는다.

1. 이전·새 절대 경로와 조사할 디렉터리를 확정한다. 실제 `CLAUDE_CONFIG_DIR`와 프로젝트 설정 JSON 위치를 확인하고 홈 전체·`/`를 검색하지 않는다.
2. 지정한 범위에서 절대 경로·상대 경로·홈 약칭·file URI·심링크·IDE·shell·문서·MCP 참조를 조사한다. 일반 파일의 확인한 참조만 `--reference-map FILE OLD NEW`로 지정한다. 세션 JSONL을 일반 텍스트 전체 치환에 넣지 않는다.
3. 스크립트는 프로젝트 소속을 확인해 `projects/<encoded-path>`를 새 경로 이름으로 옮기고, JSONL의 경로 메타데이터, `sessions-index.json`, 설정 JSON의 `projects` 키, `history.jsonl`의 `project`, 해당 ID의 task/file-history 메타데이터를 자동 갱신한다. 메모리·하위 파일을 유지한다. 세션 ID·메시지 UUID·타임스탬프·본문·도구 입력/결과는 바꾸지 않는다.
4. 계획의 폴더·파일 목록과 diff, 백업 위치·SHA256을 보여주고 승인받는다. 인코딩 충돌·기존 목적지·알 수 없는 소속·잘못된 JSON은 변경 전에 중단한다.

```bash
uv run --python 3.11 python <플러그인 경로>/scripts/claude_rename.py plan \
  --source /absolute/old --destination /absolute/new \
  --claude-home /actual/claude --claude-config /actual/claude.json \
  --out /outside/project/claude-rename-plan
uv run --python 3.11 python <플러그인 경로>/scripts/claude_rename.py apply --plan /outside/project/claude-rename-plan/plan.json --approve <계획 SHA256>
uv run --python 3.11 python <플러그인 경로>/scripts/claude_rename.py verify --plan /outside/project/claude-rename-plan/plan.json
uv run --python 3.11 python <플러그인 경로>/scripts/claude_rename.py rollback --plan /outside/project/claude-rename-plan/plan.json --approve <같은 SHA256>
```

`--out`은 프로젝트·세션 저장소 밖의 새 디렉터리다. 참조 파일의 변경 전/후 원문을 보관하며 비밀을 응답에 노출하지 않는다. 설정 JSON이 있으면 `--claude-config`를 지정하고 없음을 확인했을 때만 생략한다. 다른 스킬이 이미 폴더를 rename했다면 plan에 `--sessions-only`를 추가해 Claude 경로만 갱신한다.

기록 중인 파일은 적용 전에 차단한다. 프로세스를 종료·재시작하거나 PID에 신호를 보내지 않는다. 파일을 계속 쓰는 상태라면 사용자가 기록을 마친 뒤 같은 계획의 유효성을 확인하거나 새 계획을 만든다. 스크립트는 현재 Linux의 writer 검사를 사용한다. 검사 불가 상태에서 우회하지 않는다.

검증은 저장 파일·세션 ID·기존 메시지/도구 결과와 갱신된 경로를 대조한다. 새 세션·새 대화·검증 메시지를 만들지 않는다. 일반 rename은 디렉터리 자체를 옮겨 숨김·미커밋 파일을 유지한다. 실패하면 수정한 경로와 폴더 이름을 복구하되 이후 사용자 변경을 덮어쓰지 않는다. 다른 도구(Codex) 세션이 같은 프로젝트에 있으면 그 도구의 별도 스킬도 적용해야 전체 이관 완료다. 결과에 기존 세션 ID 유지·대화 보존·자동 갱신 범위·남은 외부 참조·백업 위치를 보고한다.
