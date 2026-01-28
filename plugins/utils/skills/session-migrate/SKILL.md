---
name: session-migrate
description: "Claude Code 세션 대화 기록을 다른 프로젝트로 마이그레이션. MUST use when user: (1) asks to move/migrate/copy session, (2) mentions '세션 옮기기/복사', (3) wants to transfer conversation history to another project."
context: fork
agent: general-purpose
allowed-tools:
  - Bash(pwd)
  - Bash(dirname *)
  - Bash(basename *)
  - Bash(ls *)
  - Bash(stat *)
  - Bash(find *)
  - Bash(cp *)
  - Bash(mkdir *)
  - Bash(rm *)
  - Bash(sed *)
  - Bash(echo *)
  - Bash(grep *)
  - Bash(head *)
  - Bash(tail *)
  - Bash(cut *)
  - Bash(wc *)
  - Read
  - Write
---

# Session Migrate

Claude Code의 세션 대화 기록을 다른 프로젝트로 마이그레이션합니다.

## Quick Start

```bash
# 스킬 실행 (대화형으로 파라미터 수집)
/session-migrate

# 또는 직접 질문 받기
세션을 다른 프로젝트로 옮겨줘
현재 세션을 /path/to/project로 복사해줘
```

## Core Workflow

### Step 1: 초기 설정 (탭 형식 질문)

사용자에게 소스, 목적지, 범위를 한번에 질문합니다.

먼저 현재 작업 디렉토리를 확인합니다.

```bash
CURRENT_DIR=$(pwd)
PARENT_DIR=$(dirname "$CURRENT_DIR")
```

그다음 AskUserQuestion으로 3개 질문을 탭 형식으로 표시합니다.

```
AskUserQuestion:
  questions:
    - question: "소스 프로젝트 경로를 선택하세요"
      header: "소스"
      multiSelect: false
      options:
        - label: "현재 프로젝트 (Recommended)"
          description: "$CURRENT_DIR의 세션을 복사"
        - label: "상위 프로젝트"
          description: "$PARENT_DIR의 세션을 복사"
        # Other 옵션은 자동으로 추가됨 (다른 경로 직접 입력)

    - question: "목적지 프로젝트 경로를 선택하세요"
      header: "목적지"
      multiSelect: false
      options:
        - label: "현재 프로젝트 (Recommended)"
          description: "$CURRENT_DIR로 세션을 복사"
        - label: "상위 프로젝트"
          description: "$PARENT_DIR로 세션을 복사"
        # Other 옵션은 자동으로 추가됨 (다른 경로 직접 입력)

    - question: "어떤 세션을 마이그레이션할까요?"
      header: "범위"
      multiSelect: false
      options:
        - label: "전체 세션 (Recommended)"
          description: "모든 세션 대화 기록을 복사"
        - label: "가장 최근 세션 1개"
          description: "가장 최근 수정된 세션 1개만 복사"
        # Other 옵션은 자동으로 추가됨
        # 안내: "최근 N개 (숫자 입력) 또는 검색어 입력 가능"
```

**변수 설정:**
- `SOURCE_PROJECT`: 선택한 프로젝트 절대 경로
- `TARGET_PROJECT`: 선택한 프로젝트 절대 경로
- `MIGRATION_MODE`:
  - "전체 세션" → `all`
  - "가장 최근 세션 1개" → `recent_one`
  - Other 입력값이 숫자 → `recent` (SESSION_COUNT 설정)
  - Other 입력값이 문자열 → `search` (SEARCH_QUERY 설정)

### Step 2: 기존 세션 처리 방식 선택

목적지 프로젝트 폴더에 이미 세션이 존재하는지 확인합니다.

```bash
# 1. 입력 경로 정규화 (끝의 / 제거)
NORMALIZED_TARGET="${TARGET_PROJECT%/}"

# 2. 목적지 폴더 경로 계산
# IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
EXPECTED_TARGET_FOLDER=$(echo "$NORMALIZED_TARGET" | sed 's|[^a-zA-Z0-9]|-|g')
TARGET_FOLDER=~/.claude/projects/$EXPECTED_TARGET_FOLDER

# 3. sessions-index.json 존재 여부 확인
if [ -f "$TARGET_FOLDER/sessions-index.json" ]; then
  # 기존 세션 수 확인
  EXISTING_COUNT=$(ls -1 $TARGET_FOLDER/*.jsonl 2>/dev/null | wc -l)
  echo "⚠️  목적지에 이미 $EXISTING_COUNT개의 세션 존재"
else
  echo "✅ 목적지는 새 폴더 (기존 세션 없음)"
  EXISTING_COUNT=0
fi
```

**기존 세션이 있는 경우에만** 다음 질문을 표시:

```
AskUserQuestion:
  question: "목적지에 이미 [N]개의 세션이 있습니다. 어떻게 처리할까요?"
  header: "처리 방식"
  multiSelect: false
  options:
    - label: "추가 (Recommended)"
      description: "기존 세션 유지하고 새 세션 추가"
    - label: "덮어쓰기"
      description: "기존 세션 모두 삭제하고 새로 복사"
    - label: "취소"
      description: "마이그레이션 취소"
```

**변수 설정:**
- `MERGE_MODE`: `append` / `overwrite` / `cancel`
- `append`: 기존 세션은 유지하고 새 세션 추가 (세션 ID 중복 시 건너뛰기)
- `overwrite`: 목적지 폴더의 모든 세션 삭제 후 복사
- `cancel`: 작업 취소

**기존 세션이 없는 경우:**
- 자동으로 `MERGE_MODE = append`로 설정하고 다음 단계로 진행

### Step 3: 소스 프로젝트 세션 확인

소스 프로젝트 폴더를 찾습니다. 사용자 입력이 애매할 수 있으므로 robust하게 검색합니다.

```bash
# 1. 입력 경로 정규화 (끝의 / 제거)
NORMALIZED_SOURCE="${SOURCE_PROJECT%/}"

# 2. 정확한 폴더명 계산
# IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
EXPECTED_FOLDER=$(echo "$NORMALIZED_SOURCE" | sed 's|[^a-zA-Z0-9]|-|g')
SOURCE_FOLDER=~/.claude/projects/$EXPECTED_FOLDER

# 3. 정확한 폴더 검색
if [ -d "$SOURCE_FOLDER" ]; then
  TOTAL_SESSIONS=$(ls -1 $SOURCE_FOLDER/*.jsonl 2>/dev/null | wc -l)
  if [ $TOTAL_SESSIONS -gt 0 ]; then
    echo "✅ 소스 폴더 발견: $TOTAL_SESSIONS개 세션"
  else
    echo "❌ 오류: 소스 프로젝트에 세션이 없습니다."
    exit 1
  fi
else
  # 4. 유사한 폴더 검색
  echo "정확한 폴더를 찾지 못함. 유사한 폴더 검색 중..."

  # 프로젝트명 추출 (경로의 마지막 부분)
  PROJECT_NAME=$(basename "$NORMALIZED_SOURCE")

  # 유사한 폴더 찾기 (대소문자 무시, 부분 매칭)
  SIMILAR_FOLDERS=$(find ~/.claude/projects -maxdepth 1 -type d -iname "*${PROJECT_NAME}*" 2>/dev/null)

  if [ -z "$SIMILAR_FOLDERS" ]; then
    echo "❌ 오류: '$PROJECT_NAME' 관련 폴더를 찾을 수 없습니다."
    exit 1
  fi

  # 세션이 있는 폴더만 필터링
  FOLDERS_WITH_SESSIONS=""
  while IFS= read -r folder; do
    SESSION_COUNT=$(ls -1 "$folder"/*.jsonl 2>/dev/null | wc -l)
    if [ $SESSION_COUNT -gt 0 ]; then
      FOLDERS_WITH_SESSIONS="$FOLDERS_WITH_SESSIONS$folder|$SESSION_COUNT
"
    fi
  done <<< "$SIMILAR_FOLDERS"

  if [ -z "$FOLDERS_WITH_SESSIONS" ]; then
    echo "❌ 오류: 세션이 있는 폴더를 찾을 수 없습니다."
    exit 1
  fi

  # 하나만 있으면 자동 선택
  FOLDER_COUNT=$(echo "$FOLDERS_WITH_SESSIONS" | grep -c .)
  if [ $FOLDER_COUNT -eq 1 ]; then
    SOURCE_FOLDER=$(echo "$FOLDERS_WITH_SESSIONS" | cut -d'|' -f1)
    TOTAL_SESSIONS=$(echo "$FOLDERS_WITH_SESSIONS" | cut -d'|' -f2)
    echo "✅ 유사 폴더 자동 선택: $(basename $SOURCE_FOLDER) ($TOTAL_SESSIONS 세션)"
  else
    # 여러 개 있으면 사용자 선택
    echo "⚠️  여러 유사 폴더 발견:"
    echo "$FOLDERS_WITH_SESSIONS"

    # AskUserQuestion으로 선택
    # (Task 에이전트에서 처리)
    exit 2
  fi
fi
```

**변수 설정:**
- `SOURCE_FOLDER`: 최종 선택된 소스 폴더 경로
- `TOTAL_SESSIONS`: 소스 폴더의 총 세션 개수

**Exit 코드:**
- `0`: 성공
- `1`: 폴더를 찾을 수 없거나 세션이 없음
- `2`: 여러 유사 폴더 발견 (사용자 선택 필요)

---

## Task Agent Execution

모든 파라미터 수집 후 Task 에이전트를 실행하여 실제 마이그레이션을 수행합니다.

**IMPORTANT**: Task 실행 시 반드시 `allowedPrompts`를 포함하여 사용자 권한 요청을 최소화해야 합니다.

### Allowed Prompts (모든 모드 공통)

```typescript
allowedPrompts: [
  { tool: "Bash", prompt: "프로젝트 경로를 폴더명으로 변환" },
  { tool: "Bash", prompt: "소스/목적지 폴더 경로 계산" },
  { tool: "Bash", prompt: "세션 파일 목록 조회" },
  { tool: "Bash", prompt: "세션 파일 복사" },
  { tool: "Bash", prompt: "목적지 폴더 생성" },
  { tool: "Bash", prompt: "기존 세션 삭제" },
  { tool: "Bash", prompt: "파일 내 경로 변경" },
  { tool: "Bash", prompt: "파일 메타데이터 확인" },
  { tool: "Bash", prompt: "세션 ID 추출" },
  { tool: "Bash", prompt: "변수 설정 및 조건 확인" }
]
```

### Recent Mode (최근 세션 N개)

```
Task(subagent_type="general-purpose"):
  allowedPrompts: [
    { tool: "Bash", prompt: "프로젝트 경로를 폴더명으로 변환" },
    { tool: "Bash", prompt: "소스/목적지 폴더 경로 계산" },
    { tool: "Bash", prompt: "세션 파일 목록 조회" },
    { tool: "Bash", prompt: "세션 파일 복사" },
    { tool: "Bash", prompt: "목적지 폴더 생성" },
    { tool: "Bash", prompt: "기존 세션 삭제" },
    { tool: "Bash", prompt: "파일 내 경로 변경" },
    { tool: "Bash", prompt: "파일 메타데이터 확인" },
    { tool: "Bash", prompt: "세션 ID 추출" },
    { tool: "Bash", prompt: "변수 설정 및 조건 확인" }
  ]
  프롬프트: |
    Claude Code 세션을 마이그레이션해주세요.

    **파라미터:**
    - 소스 프로젝트: [SOURCE_PROJECT]
    - 목적지 프로젝트: [TARGET_PROJECT]
    - 마이그레이션 모드: 최근 세션 N개
    - 세션 개수: [SESSION_COUNT]
    - 병합 모드: [MERGE_MODE] (append/overwrite)

    **수행 작업:**

    0. (overwrite 모드인 경우) 기존 세션 삭제
       ```bash
       if [ "[MERGE_MODE]" = "overwrite" ]; then
         # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
         TARGET_FOLDER=~/.claude/projects/$(echo "[TARGET_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
         rm -rf $TARGET_FOLDER/*
       fi
       ```

    1. 소스 프로젝트 폴더 경로 계산
       ```bash
       # 경로를 Claude 프로젝트 폴더명으로 변환
       # /home/user/project_name → -home-user-project-name (모든 특수문자 dash로)
       # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
       SOURCE_FOLDER=~/.claude/projects/$(echo "[SOURCE_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
       ```

    2. 최근 세션 파일들 찾기
       ```bash
       # 가장 최근 수정된 N개의 .jsonl 파일
       RECENT_SESSIONS=$(ls -t $SOURCE_FOLDER/*.jsonl | head -n [SESSION_COUNT])
       ```

    3. sessions-index.json에서 세션 정보 추출
       ```bash
       # Read 도구로 sessions-index.json 읽기
       # 각 세션의 summary, firstPrompt 등 메타데이터 추출
       ```

    4. 목적지 프로젝트 폴더 생성
       ```bash
       # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
       TARGET_FOLDER=~/.claude/projects/$(echo "[TARGET_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
       mkdir -p $TARGET_FOLDER
       ```

    5. 세션 파일들 복사
       ```bash
       # 각 세션 파일 복사
       for session_file in $RECENT_SESSIONS; do
         cp $session_file $TARGET_FOLDER/
       done
       ```

    6. 파일 내 모든 경로 변경
       ```bash
       # 복사된 모든 파일의 경로 변경
       for session_file in $RECENT_SESSIONS; do
         session_id=$(basename $session_file .jsonl)
         sed -i 's|[SOURCE_PROJECT]|[TARGET_PROJECT]|g' $TARGET_FOLDER/$session_id.jsonl
       done
       ```

    7. sessions-index.json 업데이트
       ```bash
       # append 모드: 기존 sessions-index.json 읽기 (있으면)
       if [ "[MERGE_MODE]" = "append" ] && [ -f "$TARGET_FOLDER/sessions-index.json" ]; then
         # Read 도구로 기존 sessions-index.json 읽기
         # 기존 entries 배열에 새 엔트리 추가
       else
         # overwrite 모드 또는 기존 파일 없음: 새로 생성
       fi

       # Write 도구로 업데이트된 sessions-index.json 저장
       # 각 세션에 대해 엔트리 추가:
       for session_file in $RECENT_SESSIONS; do
         session_id=$(basename $session_file .jsonl)
         # 새 엔트리 필드:
         # - sessionId (소스에서 복사)
         # - fullPath: $TARGET_FOLDER/$session_id.jsonl
         # - fileMtime (현재 파일의 mtime)
         # - firstPrompt (소스에서 복사)
         # - summary (소스에서 복사)
         # - messageCount (소스에서 복사)
         # - created (소스에서 복사)
         # - modified (현재 시간)
         # - gitBranch (소스에서 복사 또는 "main")
         # - projectPath: [TARGET_PROJECT]
         # - isSidechain: false
       done
       # - originalPath: [TARGET_PROJECT]

       # 중복 검사 (append 모드):
       # - 동일한 sessionId가 이미 있으면 건너뛰기
       ```

    **반환 형식:**
    ```
    ✅ 최근 세션 [SESSION_COUNT]개 마이그레이션 완료

    - 소스: [SOURCE_PROJECT]
    - 목적지: [TARGET_PROJECT]
    - 마이그레이션된 세션: [N]개
      - [세션1 요약] ([M1]개 메시지)
      - [세션2 요약] ([M2]개 메시지)
      - ...
    ```
```

### All Mode (전체 세션)

```
Task(subagent_type="general-purpose"):
  allowedPrompts: [
    { tool: "Bash", prompt: "프로젝트 경로를 폴더명으로 변환" },
    { tool: "Bash", prompt: "소스/목적지 폴더 경로 계산" },
    { tool: "Bash", prompt: "세션 파일 목록 조회" },
    { tool: "Bash", prompt: "세션 파일 복사" },
    { tool: "Bash", prompt: "목적지 폴더 생성" },
    { tool: "Bash", prompt: "기존 세션 삭제" },
    { tool: "Bash", prompt: "파일 내 경로 변경" },
    { tool: "Bash", prompt: "파일 메타데이터 확인" },
    { tool: "Bash", prompt: "세션 ID 추출" },
    { tool: "Bash", prompt: "변수 설정 및 조건 확인" }
  ]
  프롬프트: |
    Claude Code의 모든 세션을 마이그레이션해주세요.

    **파라미터:**
    - 소스 프로젝트: [SOURCE_PROJECT]
    - 목적지 프로젝트: [TARGET_PROJECT]
    - 마이그레이션 모드: 전체 세션
    - 병합 모드: [MERGE_MODE] (append/overwrite)

    **수행 작업:**

    0. (overwrite 모드인 경우) 기존 세션 삭제
       ```bash
       if [ "[MERGE_MODE]" = "overwrite" ]; then
         # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
         TARGET_FOLDER=~/.claude/projects/$(echo "[TARGET_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
         rm -rf $TARGET_FOLDER/*
       fi
       ```

    1. 소스/목적지 프로젝트 폴더 경로 계산
       ```bash
       # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
       SOURCE_FOLDER=~/.claude/projects/$(echo "[SOURCE_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
       TARGET_FOLDER=~/.claude/projects/$(echo "[TARGET_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
       mkdir -p $TARGET_FOLDER
       ```

    2. 모든 세션 파일 복사 (append 모드인 경우 중복 체크)
       ```bash
       cp $SOURCE_FOLDER/*.jsonl $TARGET_FOLDER/
       ```

    3. 모든 파일의 경로 변경
       ```bash
       sed -i 's|[SOURCE_PROJECT]|[TARGET_PROJECT]|g' $TARGET_FOLDER/*.jsonl
       ```

    4. sessions-index.json 복사 및 수정
       ```bash
       # Read 도구로 소스 sessions-index.json 읽기
       # 모든 엔트리의 projectPath를 [TARGET_PROJECT]로 변경
       # fullPath를 새 폴더 경로로 변경
       # originalPath를 [TARGET_PROJECT]로 변경

       # append 모드: 기존 sessions-index.json과 병합
       if [ "[MERGE_MODE]" = "append" ] && [ -f "$TARGET_FOLDER/sessions-index.json" ]; then
         # Read 도구로 기존 sessions-index.json 읽기
         # 기존 entries와 새 entries 병합
         # 중복 sessionId는 건너뛰기
       fi

       # Write 도구로 저장
       ```

    5. 세션 폴더도 복사 (있는 경우)
       ```bash
       # sessions-index.json에서 디렉토리가 있는 세션 확인
       # 해당 디렉토리들을 목적지로 복사
       # 디렉토리 내 파일들도 경로 변경
       ```

    **반환 형식:**
    ```
    ✅ 전체 세션 마이그레이션 완료

    - 소스: [SOURCE_PROJECT]
    - 목적지: [TARGET_PROJECT]
    - 마이그레이션된 세션: [N]개
    - 총 메시지: [M]개
    ```
```

### Search Mode (특정 세션 검색)

```
Task(subagent_type="general-purpose"):
  allowedPrompts: [
    { tool: "Bash", prompt: "프로젝트 경로를 폴더명으로 변환" },
    { tool: "Bash", prompt: "소스/목적지 폴더 경로 계산" },
    { tool: "Bash", prompt: "세션 파일 목록 조회" },
    { tool: "Bash", prompt: "세션 파일 복사" },
    { tool: "Bash", prompt: "목적지 폴더 생성" },
    { tool: "Bash", prompt: "기존 세션 삭제" },
    { tool: "Bash", prompt: "파일 내 경로 변경" },
    { tool: "Bash", prompt: "파일 메타데이터 확인" },
    { tool: "Bash", prompt: "세션 ID 추출" },
    { tool: "Bash", prompt: "변수 설정 및 조건 확인" }
  ]
  프롬프트: |
    Claude Code 세션을 검색하여 마이그레이션해주세요.

    **파라미터:**
    - 소스 프로젝트: [SOURCE_PROJECT]
    - 목적지 프로젝트: [TARGET_PROJECT]
    - 마이그레이션 모드: 검색
    - 병합 모드: [MERGE_MODE] (append/overwrite)
    - 검색어: [SEARCH_QUERY]

    **수행 작업:**

    0. (overwrite 모드인 경우) 기존 세션 삭제
       ```bash
       if [ "[MERGE_MODE]" = "overwrite" ]; then
         # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
         TARGET_FOLDER=~/.claude/projects/$(echo "[TARGET_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
         rm -rf $TARGET_FOLDER/*
       fi
       ```

    1. 소스 프로젝트 폴더 경로 계산
       ```bash
       # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
       SOURCE_FOLDER=~/.claude/projects/$(echo "[SOURCE_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
       ```

    2. sessions-index.json에서 검색
       ```bash
       # Read 도구로 sessions-index.json 읽기
       # firstPrompt, summary에서 [SEARCH_QUERY] 검색
       # 매칭되는 세션 ID 목록 추출
       ```

    3. 검색 결과 표시 및 선택
       ```
       AskUserQuestion:
         question: "다음 세션 중 마이그레이션할 세션을 선택하세요"
         header: "세션 선택"
         multiSelect: true
         options:
           - label: "[세션1 요약]"
             description: "메시지 [N]개, 수정일: [DATE]"
           - label: "[세션2 요약]"
             description: "메시지 [M]개, 수정일: [DATE]"
           ...
       ```

    4. 선택된 세션들 마이그레이션
       ```bash
       # 목적지 폴더 생성
       # IMPORTANT: 모든 특수문자(_포함)를 - 로 변환
       TARGET_FOLDER=~/.claude/projects/$(echo "[TARGET_PROJECT]" | sed 's|[^a-zA-Z0-9]|-|g')
       mkdir -p $TARGET_FOLDER

       # 각 선택된 세션 파일 복사
       for session_id in [SELECTED_SESSION_IDS]; do
         cp $SOURCE_FOLDER/$session_id.jsonl $TARGET_FOLDER/

         # 경로 변경
         sed -i 's|[SOURCE_PROJECT]|[TARGET_PROJECT]|g' $TARGET_FOLDER/$session_id.jsonl
       done

       # sessions-index.json 업데이트
       # append 모드: 기존 sessions-index.json과 병합
       if [ "[MERGE_MODE]" = "append" ] && [ -f "$TARGET_FOLDER/sessions-index.json" ]; then
         # Read 도구로 기존 sessions-index.json 읽기
         # 기존 entries와 새 entries 병합
         # 중복 sessionId는 건너뛰기
       else
         # overwrite 모드 또는 기존 파일 없음: 새로 생성
       fi
       # Write 도구로 저장
       ```

    **반환 형식:**
    ```
    ✅ 선택한 세션 마이그레이션 완료

    - 소스: [SOURCE_PROJECT]
    - 목적지: [TARGET_PROJECT]
    - 마이그레이션된 세션: [N]개
      - [세션1 요약] ([M1]개 메시지)
      - [세션2 요약] ([M2]개 메시지)
    ```
```

---

## Implementation Details

### 프로젝트 경로 → 폴더명 변환

```bash
# 모든 특수문자(/, _, 등)를 - 로 변환
FOLDER_NAME=$(echo "$PROJECT_PATH" | sed 's|[^a-zA-Z0-9]|-|g')
```

### 폴더 검색 로직

1. 입력 정규화 (끝의 `/` 제거)
2. 정확한 경로로 검색
3. 없으면 프로젝트명으로 유사 검색 (`find -iname`)
4. 세션 있는 폴더만 필터링
5. 1개면 자동 선택, 여러 개면 사용자 선택

## Important Rules

- 경로 변환: `sed 's|[^a-zA-Z0-9]|-|g'` (모든 특수문자 → dash)
- 원본 파일 유지, 복사 후 경로 변경
- sessions-index.json 업데이트 필수
- 에러 시 명확한 메시지, all-or-nothing 원칙
