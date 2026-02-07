---
description: Launch cote-writer agent to create a Baekjoon problem write-up from Python solution files (single or batch mode)
allowed-tools:
  - Read
  - Write
  - Bash(cat *)
  - Bash(pwd)
  - Bash(ls *)
  - Bash(mkdir *)
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
---

# Coding Test Problem Write-up Flow

## Step 1: Read Configuration and Environment

```bash
# Check current config
cat ~/.config/claude-code/docs_config.json 2>/dev/null || echo "NO_CONFIG"

# Get current directory
pwd
```

Store these values:
- `{config}`: Parsed config object or defaults
- `{current_directory}`: Current working directory
- `{base_path}`: config.base_path or "~/Documents/docs"
- `{cote_folder}`: config.folders.cote or "cote"
- `{cote_template}`: config.cote_template or "default"

## Step 2: Find ALL Python Files

Find all `.py` files in the current directory and subdirectories:

```bash
ls -t *.py 2>/dev/null
```

If no `.py` file found in current directory, try `py/` subdirectory:
```bash
ls -t py/*.py 2>/dev/null
```

Store:
- `{all_py_files}`: List of all found .py files (sorted by modification time, newest first)
- `{py_file_count}`: Number of .py files found
- If no .py file found → Output error and stop: "현재 디렉토리에서 .py 파일을 찾을 수 없습니다."

## Step 3: Select Mode (파일 선택)

**파일이 1개인 경우**: 질문 건너뛰고 바로 해당 파일로 진행 (단일 모드)

**파일이 2개 이상인 경우**: AskUserQuestion으로 선택

```
Question: "{py_file_count}개의 .py 파일을 발견했습니다. 어떻게 처리할까요?"
Header: "처리 모드"
Options:
  - label: "전체 파일", description: "발견된 {py_file_count}개 파일 모두 정리 (병렬 실행)"
  - label: "최신 파일만", description: "{newest_file} 파일만 정리"
multiSelect: false
```

Store:
- `{mode}`: "batch" or "single"
- `{target_files}`: 처리할 파일 목록

## Step 4: Validate Files and Extract Info

각 대상 파일에 대해:

1. **Read the file**
2. **First line**: Extract Baekjoon URL
   - Expected format: `# https://www.acmicpc.net/problem/{number}`
   - URL이 없는 파일 → 스킵하고 경고 메시지 출력
3. **Rest of file**: User's solution code

Store per file:
- `{py_file_path}`: Path to the .py file
- `{problem_url}`: Full Baekjoon URL
- `{problem_number}`: Extracted problem number
- `{user_code}`: The solution code (without the URL comment line)

## Step 5: Determine Output Path

Resolve output path:

1. If config has `base_path` and `folders.cote`:
   - `{output_path}` = `{base_path}/{cote_folder}/`
2. Else:
   - `{output_path}` = `{current_directory}/docs/cote/`

## Step 6: Launch Agent(s)

### Single Mode (파일 1개)

Use the Task tool with subagent_type='docs:cote-writer':

**Prompt format:**
```
py 파일 경로: {py_file_path}
문제 URL: {problem_url}
내 코드:
{user_code}
저장 경로: {output_path}
템플릿: {cote_template}
```

### Batch Mode (파일 여러 개)

**CRITICAL**: 각 파일별로 개별 Task 에이전트를 **병렬로** 실행한다.
devlog 커맨드의 병렬 Task 패턴을 따른다.

For each validated file, launch a Task tool with subagent_type='docs:cote-writer':

**Prompt format for EACH agent:**
```
py 파일 경로: {py_file_path}
문제 URL: {problem_url}
내 코드:
{user_code}
저장 경로: {output_path}
템플릿: {cote_template}
```

**Example**: 3개 파일이 있는 경우:

```
Task 1:
- subagent_type: 'docs:cote-writer'
- prompt: "py 파일 경로: /home/user/py/17609.py\n문제 URL: https://www.acmicpc.net/problem/17609\n내 코드:\nimport sys...\n저장 경로: ~/Documents/docs/cote/\n템플릿: default"

Task 2:
- subagent_type: 'docs:cote-writer'
- prompt: "py 파일 경로: /home/user/py/1234.py\n문제 URL: https://www.acmicpc.net/problem/1234\n내 코드:\nfrom collections...\n저장 경로: ~/Documents/docs/cote/\n템플릿: default"

Task 3:
- subagent_type: 'docs:cote-writer'
- prompt: "py 파일 경로: /home/user/py/5678.py\n문제 URL: https://www.acmicpc.net/problem/5678\n내 코드:\nn = int(input())...\n저장 경로: ~/Documents/docs/cote/\n템플릿: default"
```

**IMPORTANT**: Launch all agents in parallel using multiple Task tool calls in a single response message.

## Step 7: Summary Report (배치 모드 시)

배치 모드 완료 후 요약 리포트를 출력한다:

```
코딩테스트 문제 정리가 완료되었습니다.

처리 결과:
- ✅ {number}번 {title} → {file_path}
- ✅ {number}번 {title} → {file_path}
- ⚠️ {filename}: URL 없음 (스킵)

총 {success_count}/{total_count}개 파일 처리 완료
저장 위치: {output_path}
```

## Quick Reference

```
/docs:cote 실행 흐름:
1. config 읽기
2. 전체 .py 파일 탐색
3. 1개 → 바로 진행 / N개 → AskUserQuestion (전체/최신)
4. URL + 코드 추출 (유효성 검증)
5. 저장 경로 결정
6. 에이전트 실행 (단일 또는 병렬)
7. 배치 시 요약 리포트
```

## Examples

**Normal execution (단일 파일):**
```
User: /docs:cote

→ Config: base_path=~/Documents/docs, cote_folder=cote
→ pwd: /home/user/algorithm
→ ls -t py/*.py → py/17609.py (1개)
→ 질문 생략, 바로 진행
→ Read py/17609.py:
    Line 1: # https://www.acmicpc.net/problem/17609
    Rest: import sys ...
→ Output path: ~/Documents/docs/cote/
→ Task: cote-writer (1개)
```

**Batch execution (전체 파일):**
```
User: /docs:cote

→ pwd: /home/user/algorithm
→ ls -t py/*.py → py/17609.py py/1234.py py/5678.py (3개)
→ AskUserQuestion: "3개의 .py 파일을 발견했습니다. 어떻게 처리할까요?"
   User: "전체 파일"
→ 각 파일 URL 검증 (17609, 1234 OK / 5678 URL 없음 → 스킵)
→ Output path: ~/Documents/docs/cote/
→ Task 1: cote-writer (17609.py) ─┐
→ Task 2: cote-writer (1234.py)  ─┤ 병렬 실행
→ 요약 리포트: 2/3 성공, 1 스킵
```

**Single file selection from batch:**
```
User: /docs:cote

→ ls -t py/*.py → py/17609.py py/1234.py (2개)
→ AskUserQuestion: "2개의 .py 파일을 발견했습니다."
   User: "최신 파일만"
→ py/17609.py만 처리
→ Task: cote-writer (1개)
```

**No config (defaults):**
```
User: /docs:cote

→ Config: NO_CONFIG → use defaults
→ pwd: /home/user/algorithm
→ ls -t *.py → 17609.py (1개)
→ Output path: /home/user/algorithm/docs/cote/
→ Task: cote-writer ...
```

**Error - no py file:**
```
User: /docs:cote

→ ls -t *.py → (empty)
→ ls -t py/*.py → (empty)
→ Output: "현재 디렉토리에서 .py 파일을 찾을 수 없습니다."
```

**Error - no URL in file:**
```
User: /docs:cote

→ ls -t *.py → solution.py (1개)
→ Read solution.py → Line 1: import sys (no URL)
→ Output: "py 파일 첫 줄에 백준 문제 URL을 # 주석으로 추가해주세요."
```
