---
name: mv-project
description: 사용자가 전체 프로젝트 폴더 및 Claude·Codex 세션을 함께 옮겨 달라고 할 때 사용한다. asm relocate가 폴더·세션·설정을 기계적으로 옮기고, 에이전트는 옛 경로가 남은 파일만 조사·수정한다.
---

# Move Project

“~ 전체 프로젝트 폴더 및 세션 옮겨줘”는 이 스킬이다. 세션만 옮기는 요청은 `mv-session`이다. 폴더 rename·세션 이관·`~/.claude.json`/Codex `config.toml`의 프로젝트 키·`git worktree repair`는 asm(`agent-session-manager`)의 `relocate`가 한다. 에이전트는 세션 JSONL·Codex DB·이 설정들을 직접 편집하지 않는다.

## 1. 준비

`asm relocate --help`가 실패하면 **“asm 0.16.1 이상이 필요합니다: `uv tool install --upgrade agent-session-manager`”**라고 안내하고 중단한다. 이전·새 절대 경로를 확정한다. 새 경로는 아직 없어야 하고 같은 파일시스템이어야 한다.

## 2. 계획 확인

```bash
asm relocate /absolute/old /absolute/new --dry-run --json
```

폴더, Claude 세션 수·프로젝트 디렉터리, Codex 세션 수, 바뀔 설정 키, git 여부를 사용자에게 보여 주고 승인받는다. asm이 거부하면(목적지 존재, 다른 파일시스템, 실행 중인 Claude Code·Codex가 폴더나 세션을 쓰는 중) 메시지를 그대로 전달하고 중단한다. 현재 대화가 그 폴더 안에서 실행 중이면 **“현재 대화 중인 세션의 폴더는 옮길 수 없습니다. 다른 위치의 세션에서 이 명령을 실행하세요.”**라고 안내한다. 프로세스를 끄거나 우회하지 않는다.

## 3. 실행

```bash
asm relocate /absolute/old /absolute/new --yes --json
```

결과의 `failures`가 있으면 그대로 보고한다. 세션 이관만 실패했다면 `asm move /absolute/old /absolute/new`로 다시 시도할 수 있다고 안내한다. `venv`가 true면 가상환경을 다시 만들어야 한다고(예: `uv sync`) 알린다.

## 4. 남은 참조 (AI 담당)

결과의 `references`는 새 폴더 안에서 옛 경로가 아직 적힌 파일 목록이다(asm은 고치지 않는다). 폴더 밖 참조(다른 저장소, 셸 설정, IDE 설정)가 의심되면 사용자에게 조사 범위를 확인한다. 홈 전체·`/`는 검색하지 않는다.

조사는 읽기 전용 작업자에게 맡긴다: Claude는 `project-rename:claude-renamer`(Haiku), Codex는 `codex/agents/codex-renamer.toml`의 Luna. 작업자는 파일·일치한 참조·제안 경로·근거만 돌려준다. 메인 에이전트가 파일별 변경안을 만들어 승인받은 뒤 수정한다. 상대 경로·심링크·생성 파일(lock, 빌드 산출물)은 바꾸지 말고 사유와 함께 보고한다.

## 완료

asm 결과(옮긴 세션 수, 설정 키, git repair)와 수정한 참조 파일·남겨 둔 참조를 함께 보고한다. 되돌리기는 폴더를 원래 이름으로 `asm relocate /absolute/new /absolute/old`로 다시 옮기고, 지운 원본 세션은 `asm recovery list`/`restore`로 복구한다.
