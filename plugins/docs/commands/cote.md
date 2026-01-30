---
description: Launch cote-writer agent to create a Baekjoon problem write-up from the most recent Python solution file (no interactive questions)
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
---

# Coding Test Problem Write-up Flow

## IMPORTANT: No Interactive Questions

이 커맨드는 **질문 없이 바로 실행**됩니다. 모든 정보를 자동으로 수집하여 에이전트에 전달합니다.

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

## Step 2: Find Most Recent Python File

Find the most recently modified `.py` file in the current directory:

```bash
ls -t *.py 2>/dev/null | head -1
```

If no `.py` file found in current directory, try `py/` subdirectory:
```bash
ls -t py/*.py 2>/dev/null | head -1
```

Store:
- `{py_file_path}`: Path to the most recent .py file
- If no .py file found → Output error and stop: "현재 디렉토리에서 .py 파일을 찾을 수 없습니다."

## Step 3: Read Python File and Extract Info

Read the found `.py` file:

1. **First line**: Extract Baekjoon URL
   - Expected format: `# https://www.acmicpc.net/problem/{number}`
   - If not found → Output error: "py 파일 첫 줄에 백준 문제 URL을 # 주석으로 추가해주세요. 예: # https://www.acmicpc.net/problem/17609"
2. **Rest of file**: User's solution code

Store:
- `{problem_url}`: Full Baekjoon URL
- `{problem_number}`: Extracted problem number
- `{user_code}`: The solution code (without the URL comment line)

## Step 4: Determine Output Path

Resolve output path:

1. If config has `base_path` and `folders.cote`:
   - `{output_path}` = `{base_path}/{cote_folder}/`
2. Else:
   - `{output_path}` = `{current_directory}/docs/cote/`

## Step 5: Launch Agent

After collecting all info automatically, use the Task tool with subagent_type='docs:cote-writer':

**Prompt format for agent:**
```
py 파일 경로: {py_file_path}
문제 URL: {problem_url}
내 코드:
{user_code}
저장 경로: {output_path}
```

## Quick Reference

```
/docs:cote 실행 흐름:
1. config 읽기
2. 최신 .py 파일 찾기
3. URL + 코드 추출
4. 저장 경로 결정
5. cote-writer 에이전트 실행 (질문 없이)
```

## Examples

**Normal execution:**
```
User: /docs:cote

→ Config: base_path=~/Documents/docs, cote_folder=cote
→ pwd: /home/user/algorithm
→ ls -t py/*.py | head -1 → py/17609.py
→ Read py/17609.py:
    Line 1: # https://www.acmicpc.net/problem/17609
    Rest: import sys ...
→ Output path: ~/Documents/docs/cote/
→ Task: cote-writer
    py 파일 경로: /home/user/algorithm/py/17609.py
    문제 URL: https://www.acmicpc.net/problem/17609
    내 코드: import sys ...
    저장 경로: ~/Documents/docs/cote/
```

**No config (defaults):**
```
User: /docs:cote

→ Config: NO_CONFIG → use defaults
→ pwd: /home/user/algorithm
→ ls -t *.py | head -1 → 17609.py
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

→ ls -t *.py → solution.py
→ Read solution.py → Line 1: import sys (no URL)
→ Output: "py 파일 첫 줄에 백준 문제 URL을 # 주석으로 추가해주세요."
```
