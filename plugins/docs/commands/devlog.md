---
description: Launch daily-work-details-writer agent for detailed technical logs with interactive input collection
allowed-tools:
  - Read
  - Write
  - Bash(git:*)
  - Bash(mkdir:*)
  - Bash(ls:*)
  - Bash(cat:*)
  - Bash(pwd)
  - Glob
  - Grep
---

# Devlog Creation Flow

## Pre-check: Read Configuration and Current Directory

```bash
# Check current config for default path
cat ~/.config/claude-code/docs_config.json 2>/dev/null || echo "NO_CONFIG"

# Get current directory
pwd
```

Store these values:
- `{config_base_path}`: From config file or "docs"
- `{current_directory}`: Current working directory
- `{current_project_name}`: basename of current directory

## Step 1: Select Project (프로젝트 선택)

Use AskUserQuestion:

```
Question: "어떤 프로젝트의 개발일지를 작성할까요?"
Header: "프로젝트"
Options:
  - label: "{current_directory}", description: "현재 디렉토리 기반으로 git 커밋 및 코드 분석"
  - label: "대화 기반", description: "특정 프로젝트 경로 없이 대화 내용으로 작성"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: 현재 pwd 결과 (해당 디렉토리의 git 히스토리 + 코드 분석)
- 두번째 옵션: git 커밋 없이 대화 내용 기반으로 작성
- Other: 사용자가 직접 프로젝트 경로 입력

## Step 2: Select Output Path (출력 경로)

Use AskUserQuestion:

```
Question: "개발일지를 어디에 저장할까요?"
Header: "출력 경로"
Options:
  - label: "{config_base_path}/daily_work_details/", description: "설정된 기본 경로 사용"
  - label: "{current_directory}/docs/daily_work_details/", description: "현재 프로젝트 내 docs 폴더"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: configure에서 설정한 경로 (없으면 ~/Documents/docs/daily_work_details/)
- 두번째 옵션: 현재 프로젝트 디렉토리의 docs/daily_work_details/
- Other: 사용자가 직접 경로 입력

## Step 3: Select Date Range (날짜 범위 선택)

**SKIP this step if "대화 기반" was selected in Step 1.**

First, analyze the project to determine date options:

```bash
# Get the most recent log date from output directory
ls -1 {output_path}/{project_name}/*.md 2>/dev/null | sort -r | head -1

# Calculate today's date
today=$(date +%Y-%m-%d)

# Get the first commit date
git -C {project_path} log --all --reverse --format="%ad" --date=short | head -1

# Get total commit count from last log date to today (for distribution decision)
git -C {project_path} log --all --since="{last_log_date}" --until="$today" --oneline | wc -l
```

Store these values:
- `{last_log_date}`: Date from most recent log file (or "없음" if no logs exist)
- `{first_commit_date}`: Date of the first commit in the repository
- `{commit_count}`: Total commits in the potential date range

Use AskUserQuestion:

```
Question: "어느 기간의 개발일지를 작성할까요?"
Header: "날짜 범위"
Options:
  - label: "오늘만", description: "오늘 날짜의 커밋만 분석하여 개발일지 작성"
  - label: "마지막 이후", description: "마지막 로그({last_log_date}) 이후부터 오늘까지 (Recommended)"
  - label: "전체", description: "첫 커밋({first_commit_date})부터 오늘까지 전체 기록 생성"
multiSelect: false
```

**NOTE**:
- "오늘만": 오늘 날짜(today)의 커밋만 분석
- "마지막 이후": 기존 로그가 있으면 그 다음 날부터, 없으면 첫 커밋부터
- "전체": 모든 기록을 처음부터 다시 생성 (기존 파일 덮어쓰기)
- Other: 사용자가 직접 날짜 범위 입력 (예: "2025-01-01 ~ 2025-01-07")

### Date Range Resolution

**First, calculate today's date**:
```bash
today=$(date +%Y-%m-%d)
```

Based on selection:
- **"오늘만"**: `start_date` = $today, `end_date` = $today
- **"마지막 이후"**: `start_date` = day after last_log_date (or first_commit_date if no logs), `end_date` = $today
- **"전체"**: `start_date` = first_commit_date, `end_date` = $today
- **Other (custom)**: Parse user input for start and end dates

## Step 4: Get Dates with Commits

**After determining date range, identify all dates that have commits:**

```bash
# Get all unique dates with commits in the selected date range
git -C {project_path} log --all --since="{start_date}" --until="{end_date}" --format="%ad" --date=short | sort -u
```

This will return a list of dates (e.g., 2025-01-05, 2025-01-07, 2025-01-08).

Store these as `{dates_with_commits}` - an array of date strings.

**CRITICAL**: You will launch **ONE agent per date** that has commits. All agents will run in parallel.

## Step 5: Launch One Agent Per Date

**CRITICAL**: Launch **ONE agent per date** that has commits. All agents run in parallel.

For each date in `{dates_with_commits}`, launch a Task tool with subagent_type='devlog-writer':

**Prompt format for EACH agent:**
```
프로젝트 경로: [selected_project_path or "대화 기반"]
프로젝트 이름: [project_name]
출력 경로: [selected_output_path]
날짜: [SINGLE_DATE]
월: [YYYY-MM extracted from date]
추가 컨텍스트: $ARGUMENTS
```

**Example date extraction**:
```bash
# For date "2025-11-18", extract month as "2025-11"
month=$(echo "2025-11-18" | cut -d'-' -f1,2)
# Pass to agent: "월: 2025-11"
```

**Example**: If dates_with_commits = [2025-01-05, 2025-01-07, 2025-01-08], launch 3 agents in parallel:

```bash
# For each date, extract month
for date in 2025-01-05 2025-01-07 2025-01-08; do
  month=$(echo "$date" | cut -d'-' -f1,2)
  # Launch agent with: 날짜: $date, 월: $month
done
```

```
Task 1:
- subagent_type: 'devlog-writer'
- prompt: "프로젝트 경로: /home/user/myproject\n프로젝트 이름: myproject\n출력 경로: ~/Documents/docs/daily_work_details/\n날짜: 2025-01-05\n월: 2025-01\n추가 컨텍스트: [context]"

Task 2:
- subagent_type: 'devlog-writer'
- prompt: "프로젝트 경로: /home/user/myproject\n프로젝트 이름: myproject\n출력 경로: ~/Documents/docs/daily_work_details/\n날짜: 2025-01-07\n월: 2025-01\n추가 컨텍스트: [context]"

Task 3:
- subagent_type: 'devlog-writer'
- prompt: "프로젝트 경로: /home/user/myproject\n프로젝트 이름: myproject\n출력 경로: ~/Documents/docs/daily_work_details/\n날짜: 2025-01-08\n월: 2025-01\n추가 컨텍스트: [context]"
```

**IMPORTANT**:
- Launch all agents in parallel using multiple Task tool calls in a single response message
- Each agent has Bash tool access defined in its agent file (tools: Bash, ...)
- Each agent handles exactly ONE date
- Agent will automatically calculate month range for git log

**Path Resolution:**
- 프로젝트 경로가 지정된 경우 → 해당 경로에서 git log + 코드 분석
- "대화 기반" 선택 시 → git 분석 없이 대화 내용으로 작성 (날짜 범위 무시)
- 출력 경로: `{output_path}/{project_name}/YYYY-MM-DD.md`
  - 예: `~/Documents/docs/daily_work_details/myproject/2025-01-07.md`

## Examples

**Example 1: Today only**
```
User: /devlog

→ Pre-check: config 읽기, pwd 확인 (/home/user/myproject)
→ AskUserQuestion: 프로젝트?
   User: /home/user/myproject

→ AskUserQuestion: 출력 경로?
   User: 현재 프로젝트 내 docs 폴더

→ Analyze: 마지막 로그 2025-01-05, 첫 커밋 2024-12-01
→ AskUserQuestion: 날짜 범위?
   User: 오늘만

→ Get dates with commits in range: 2025-01-08 ~ 2025-01-08
   Result: [2025-01-08]

→ Launch 1 agent:
   Task: devlog-writer (날짜: 2025-01-08)
```

**Example 2: Since last log**
```
User: /devlog

→ AskUserQuestion: 프로젝트? → /home/user/myproject
→ AskUserQuestion: 출력 경로? → 기본 경로
→ Analyze: 마지막 로그 2025-01-05, 첫 커밋 2024-12-01
→ AskUserQuestion: 날짜 범위?
   User: 마지막 이후

→ Get dates with commits in range: 2025-01-06 ~ 2025-01-08
   Result: [2025-01-06, 2025-01-08]

→ Launch 2 agents in parallel:
   Task 1: devlog-writer (날짜: 2025-01-06)
   Task 2: devlog-writer (날짜: 2025-01-08)
```

**Example 3: Full history**
```
User: /devlog

→ AskUserQuestion: 프로젝트? → /home/user/myproject
→ AskUserQuestion: 출력 경로? → 기본 경로
→ Analyze: 첫 커밋 2024-12-01, 커밋 수 80개
→ AskUserQuestion: 날짜 범위?
   User: 전체

→ Get dates with commits in range: 2024-12-01 ~ 2025-01-08
   Result: [2024-12-01, 2024-12-03, ..., 2025-01-08] (20 dates)

→ Launch 20 agents in parallel:
   Task 1: devlog-writer (날짜: 2024-12-01)
   Task 2: devlog-writer (날짜: 2024-12-03)
   ...
   Task 20: devlog-writer (날짜: 2025-01-08)
```

**Example 4: Conversation-based (날짜 범위 선택 생략)**
```
User: /devlog API 리팩토링 작업 기록

→ AskUserQuestion: 프로젝트?
   User: 대화 기반

→ AskUserQuestion: 출력 경로?
   User: Other → "/home/user/notes/dev/"

→ Task: devlog-writer (날짜 범위 선택 SKIP)
   프로젝트 경로: 대화 기반
   프로젝트 이름: general
   출력 경로: /home/user/notes/dev/
   추가 컨텍스트: API 리팩토링 작업 기록
```

**Example 5: Custom date range**
```
User: /devlog

→ AskUserQuestion: 날짜 범위?
   User: Other → "2025-01-01 ~ 2025-01-03"

→ Get dates with commits in range: 2025-01-01 ~ 2025-01-03
   Result: [2025-01-01, 2025-01-02]

→ Launch 2 agents in parallel:
   Task 1: devlog-writer (날짜: 2025-01-01)
   Task 2: devlog-writer (날짜: 2025-01-02)
```
