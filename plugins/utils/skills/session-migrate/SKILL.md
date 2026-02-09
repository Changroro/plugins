---
name: session-migrate
description: "Claude Code 세션 대화 기록을 다른 프로젝트로 마이그레이션. MUST use when user: (1) asks to move/migrate/copy session, (2) mentions '세션 옮기기/복사', (3) wants to transfer conversation history to another project."
context: fork
agent: general-purpose
allowed-tools:
  - Bash(*)
  - Read
---

# Session Migrate

Claude Code 세션을 다른 프로젝트 경로로 복사합니다.

## Background

Claude Code 세션 저장 구조:
- 위치: `~/.claude/projects/<encoded-path>/`
- 경로 인코딩: 모든 비-영숫자 문자를 `-`로 변환
  - 예: `/home/user/my_project` → `-home-user-my-project`
- 세션 파일: `*.jsonl` (각 세션 1개 파일)
- 인덱스: `sessions-index.json`
- 메모리: `memory/` 디렉토리 (MEMORY.md 등)

## Workflow

### Step 1: 파라미터 결정

먼저 현재 디렉토리와 상위 디렉토리를 확인합니다.

사용자 메시지에서 소스/목적지 경로가 **둘 다 명시**되어 있으면 질문 없이 바로 Step 2로 진행합니다.
명시되지 않은 항목이 있으면 **AskUserQuestion 1회**로 모든 미결정 항목을 한번에 질문합니다.

```
AskUserQuestion:
  questions:
    - question: "소스 프로젝트 경로를 선택하세요"
      header: "소스"
      multiSelect: false
      options:
        - label: "$CURRENT_DIR (Recommended)"
          description: "현재 디렉토리의 세션을 복사"
        - label: "$PARENT_DIR"
          description: "상위 디렉토리의 세션을 복사"

    - question: "목적지 프로젝트 경로를 선택하세요"
      header: "목적지"
      multiSelect: false
      options:
        - label: "$PARENT_DIR (Recommended)"
          description: "상위 디렉토리로 복사"
        - label: "$CURRENT_DIR"
          description: "현재 디렉토리로 복사"

    - question: "목적지에 기존 세션이 있으면 어떻게 할까요?"
      header: "처리방식"
      multiSelect: false
      options:
        - label: "추가 (Recommended)"
          description: "기존 세션 유지, 새 세션만 추가 (중복 건너뜀)"
        - label: "덮어쓰기"
          description: "기존 세션 삭제 후 새로 복사"
```

**규칙:**
- 사용자가 이미 소스를 명시했으면 소스 질문 생략
- 사용자가 이미 목적지를 명시했으면 목적지 질문 생략
- 미결정 항목만 포함하여 AskUserQuestion **1회만** 호출

### Step 2: 마이그레이션 실행

**하나의 Bash 호출**로 전체 작업을 수행합니다. 중간에 사용자 확인을 묻지 않습니다.

```bash
#!/bin/bash
set -e

SOURCE_PATH="[소스 절대경로]"
TARGET_PATH="[목적지 절대경로]"
MERGE_MODE="[append 또는 overwrite]"

# 경로 인코딩
SOURCE_ENCODED=$(echo "$SOURCE_PATH" | sed 's|[^a-zA-Z0-9]|-|g')
TARGET_ENCODED=$(echo "$TARGET_PATH" | sed 's|[^a-zA-Z0-9]|-|g')
SOURCE_DIR="$HOME/.claude/projects/$SOURCE_ENCODED"
TARGET_DIR="$HOME/.claude/projects/$TARGET_ENCODED"

# 소스 검증
if [ ! -d "$SOURCE_DIR" ]; then
  echo "ERROR: 소스 폴더 없음: $SOURCE_DIR"
  echo "유사 폴더:"
  ls -d "$HOME/.claude/projects/"*"$(basename "$SOURCE_PATH")"* 2>/dev/null || echo "  없음"
  exit 1
fi

SESSION_COUNT=$(ls -1 "$SOURCE_DIR"/*.jsonl 2>/dev/null | wc -l)
if [ "$SESSION_COUNT" -eq 0 ]; then
  echo "ERROR: 소스에 세션 파일 없음"; exit 1
fi

# 덮어쓰기 모드: 기존 세션 삭제
mkdir -p "$TARGET_DIR"
if [ "$MERGE_MODE" = "overwrite" ]; then
  rm -f "$TARGET_DIR"/*.jsonl 2>/dev/null || true
  rm -f "$TARGET_DIR/sessions-index.json" 2>/dev/null || true
  echo "MODE: overwrite (기존 세션 삭제됨)"
else
  echo "MODE: append (기존 세션 유지)"
fi

# 세션 복사 (append 모드: -n으로 중복 건너뜀, overwrite 모드: 그냥 복사)
if [ "$MERGE_MODE" = "overwrite" ]; then
  cp -- "$SOURCE_DIR"/*.jsonl "$TARGET_DIR/" 2>/dev/null || true
else
  cp -n -- "$SOURCE_DIR"/*.jsonl "$TARGET_DIR/" 2>/dev/null || true
fi
COPIED=$(ls -1 "$TARGET_DIR"/*.jsonl 2>/dev/null | wc -l)

# 메모리 복사
if [ -d "$SOURCE_DIR/memory" ]; then
  cp -rn -- "$SOURCE_DIR/memory/" "$TARGET_DIR/memory/" 2>/dev/null || true
  echo "MEMORY: copied"
else
  echo "MEMORY: none"
fi

# sessions-index.json 복사
if [ -f "$SOURCE_DIR/sessions-index.json" ]; then
  if [ "$MERGE_MODE" = "overwrite" ] || [ ! -f "$TARGET_DIR/sessions-index.json" ]; then
    cp -- "$SOURCE_DIR/sessions-index.json" "$TARGET_DIR/sessions-index.json"
  fi
fi

# 경로 업데이트 (소스 ≠ 목적지인 경우)
if [ "$SOURCE_PATH" != "$TARGET_PATH" ]; then
  sed -i "s|$SOURCE_PATH|$TARGET_PATH|g" "$TARGET_DIR"/*.jsonl 2>/dev/null || true
  if [ -f "$TARGET_DIR/sessions-index.json" ]; then
    sed -i "s|$SOURCE_PATH|$TARGET_PATH|g" "$TARGET_DIR/sessions-index.json"
    sed -i "s|$SOURCE_ENCODED|$TARGET_ENCODED|g" "$TARGET_DIR/sessions-index.json"
  fi
  echo "PATHS: updated"
fi

echo "DONE: $COPIED sessions migrated ($SOURCE_PATH → $TARGET_PATH)"
```

**소스 폴더를 못 찾는 경우**: 유사 폴더 목록을 출력하고, 가장 유사한 폴더를 제안합니다.

### Step 3: 결과 보고

마이그레이션 결과를 간결하게 보고합니다:

```
✅ 세션 마이그레이션 완료

| 항목 | 값 |
|------|---|
| 소스 | /path/to/source |
| 목적지 | /path/to/target |
| 세션 | N개 복사됨 |
| 메모리 | 복사됨/없음 |

💡 목적지에서 `claude --resume` 으로 세션을 이어갈 수 있습니다.
```

## Important Rules

- **원본 보존**: 복사 기반 (이동 아님)
- **추가 모드**: `cp -n`으로 기존 파일 보존, 중복 건너뜀
- **덮어쓰기 모드**: 기존 세션 삭제 후 새로 복사
- **최소 질문**: AskUserQuestion **최대 1회** (미결정 항목만 질문)
- **단일 실행**: 전체 마이그레이션을 1개 Bash 스크립트로 실행
- **경로 인코딩**: `sed 's|[^a-zA-Z0-9]|-|g'`
- **에러 시**: 유사 폴더 검색 결과 안내, 사용자에게 정확한 경로 확인 요청
