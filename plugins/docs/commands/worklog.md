---
description: Launch daily-work-writer agent to generate work logs with interactive input collection
allowed-tools:
  - Read
  - Write
  - Bash(git *)
  - Bash(mkdir *)
  - Bash(cat *)
  - Bash(pwd)
  - Glob
  - Grep
---

# Worklog Creation Flow

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
Question: "어떤 프로젝트의 업무일지를 작성할까요?"
Header: "프로젝트"
Options:
  - label: "{current_directory}", description: "현재 디렉토리 기반으로 git 커밋 분석"
  - label: "대화 기반", description: "특정 프로젝트 경로 없이 대화 내용으로 작성"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: 현재 pwd 결과 (해당 디렉토리의 git 히스토리 분석)
- 두번째 옵션: git 커밋 없이 대화 내용 기반으로 작성
- Other: 사용자가 직접 프로젝트 경로 입력

## Step 2: Select Output Path (출력 경로)

Use AskUserQuestion:

```
Question: "업무일지를 어디에 저장할까요?"
Header: "출력 경로"
Options:
  - label: "{config_base_path}/daily_work/", description: "설정된 기본 경로 사용"
  - label: "{current_directory}/docs/daily_work/", description: "현재 프로젝트 내 docs 폴더"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: configure에서 설정한 경로 (없으면 ~/Documents/docs/daily_work/)
- 두번째 옵션: 현재 프로젝트 디렉토리의 docs/daily_work/
- Other: 사용자가 직접 경로 입력

## Step 3: Select Date Range (날짜 범위 선택)

**SKIP this step if "대화 기반" was selected in Step 1.**

First, analyze the project to determine date options:

```bash
# Get the most recent log date from output directory
ls -1 {output_path}/{project_name}/*.md 2>/dev/null | sort -r | head -1

# Get the first commit date
git -C {project_path} log --all --reverse --format="%ad" --date=short | head -1

# Get total commit count from last log date to today (for distribution decision)
git -C {project_path} log --all --since="{last_log_date}" --until="today" --oneline | wc -l
```

Store these values:
- `{last_log_date}`: Date from most recent log file (or "없음" if no logs exist)
- `{first_commit_date}`: Date of the first commit in the repository
- `{commit_count}`: Total commits in the potential date range

Use AskUserQuestion:

```
Question: "어느 기간의 업무일지를 작성할까요?"
Header: "날짜 범위"
Options:
  - label: "오늘만", description: "오늘 날짜의 커밋만 분석하여 업무일지 작성"
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

Based on selection:
- **"오늘만"**: `start_date` = today, `end_date` = today
- **"마지막 이후"**: `start_date` = day after last_log_date (or first_commit_date if no logs), `end_date` = today
- **"전체"**: `start_date` = first_commit_date, `end_date` = today
- **Other (custom)**: Parse user input for start and end dates

## Step 4: Analyze and Distribute Work

**After determining date range, check if distribution is needed:**

```bash
# Count commits in the selected date range
git -C {project_path} log --all --since="{start_date}" --until="{end_date}" --oneline | wc -l

# Count unique dates with commits
git -C {project_path} log --all --since="{start_date}" --until="{end_date}" --format="%ad" --date=short | sort -u | wc -l
```

### Distribution Logic

**THRESHOLD: 50 commits or 7+ unique dates → Distribute to multiple agents**

If distribution is needed:
1. Split the date range into chunks (max 7 days per agent, or ~30 commits per agent)
2. Launch multiple agents in parallel, each handling a specific date range
3. Add 1-day padding on each side for context (e.g., if processing Jan 5-10, include Jan 4 and Jan 11 commits for "다음 계획" section)

**Example distribution for 30 days of commits:**
- Agent 1: Jan 1-7 (with padding: Dec 31 - Jan 8)
- Agent 2: Jan 8-14 (with padding: Jan 7 - Jan 15)
- Agent 3: Jan 15-21 (with padding: Jan 14 - Jan 22)
- Agent 4: Jan 22-30 (with padding: Jan 21 - Jan 31)

## Step 5: Launch Agent(s)

After collecting all inputs, use the Task tool with subagent_type='worklog-writer'.

### Single Agent (No Distribution)

**Prompt format for agent:**
```
프로젝트 경로: [selected_project_path or "대화 기반"]
프로젝트 이름: [project_name]
출력 경로: [selected_output_path]
날짜 범위: [start_date] ~ [end_date]
패딩 범위: [padding_start] ~ [padding_end]
추가 컨텍스트: $ARGUMENTS
```

### Multiple Agents (Distribution Mode)

When distributing work, launch multiple Task tools **in parallel** (in a single message):

```
# Agent 1
프로젝트 경로: /home/user/myproject
프로젝트 이름: myproject
출력 경로: ~/Documents/docs/daily_work/
날짜 범위: 2025-01-01 ~ 2025-01-07
패딩 범위: 2024-12-31 ~ 2025-01-08
추가 컨텍스트: [context]

# Agent 2
프로젝트 경로: /home/user/myproject
프로젝트 이름: myproject
출력 경로: ~/Documents/docs/daily_work/
날짜 범위: 2025-01-08 ~ 2025-01-14
패딩 범위: 2025-01-07 ~ 2025-01-15
추가 컨텍스트: [context]
```

**IMPORTANT**: Launch all agents in parallel using multiple Task tool calls in a single response message.

**Path Resolution:**
- 프로젝트 경로가 지정된 경우 → 해당 경로에서 git log 분석
- "대화 기반" 선택 시 → git 분석 없이 대화 내용으로 작성 (날짜 범위 무시)
- 출력 경로: `{output_path}/{project_name}/YYYY-MM-DD.md`
  - 예: `~/Documents/docs/daily_work/myproject/2025-01-07.md`

## Examples

**Example 1: Today only**
```
User: /worklog

→ Pre-check: config 읽기, pwd 확인 (/home/user/myproject)
→ AskUserQuestion: 프로젝트?
   User: /home/user/myproject

→ AskUserQuestion: 출력 경로?
   User: ~/Documents/docs/daily_work/

→ Analyze: 마지막 로그 2025-01-05, 첫 커밋 2024-12-01
→ AskUserQuestion: 날짜 범위?
   User: 오늘만

→ Task: worklog-writer
   프로젝트 경로: /home/user/myproject
   프로젝트 이름: myproject
   출력 경로: ~/Documents/docs/daily_work/
   날짜 범위: 2025-01-08 ~ 2025-01-08
   패딩 범위: 2025-01-07 ~ 2025-01-09
```

**Example 2: Since last log (small)**
```
User: /worklog

→ AskUserQuestion: 프로젝트? → /home/user/myproject
→ AskUserQuestion: 출력 경로? → 기본 경로
→ Analyze: 마지막 로그 2025-01-05, 커밋 수 15개
→ AskUserQuestion: 날짜 범위?
   User: 마지막 이후

→ Single Task (15 commits < 50 threshold)
   날짜 범위: 2025-01-06 ~ 2025-01-08
   패딩 범위: 2025-01-05 ~ 2025-01-09
```

**Example 3: Full history (large - needs distribution)**
```
User: /worklog

→ AskUserQuestion: 프로젝트? → /home/user/myproject
→ AskUserQuestion: 출력 경로? → 기본 경로
→ Analyze: 첫 커밋 2024-12-01, 커밋 수 120개, 30일
→ AskUserQuestion: 날짜 범위?
   User: 전체

→ Distribution needed (120 commits > 50 threshold)
→ Split into 5 agents (7 days each):

→ Task 1: worklog-writer (Dec 1-7, padding: Nov 30 - Dec 8)
→ Task 2: worklog-writer (Dec 8-14, padding: Dec 7 - Dec 15)
→ Task 3: worklog-writer (Dec 15-21, padding: Dec 14 - Dec 22)
→ Task 4: worklog-writer (Dec 22-28, padding: Dec 21 - Dec 29)
→ Task 5: worklog-writer (Dec 29 - Jan 8, padding: Dec 28 - Jan 9)

(All 5 agents launched in parallel)
```

**Example 4: Conversation-based (날짜 범위 선택 생략)**
```
User: /worklog 오늘 회의 내용 정리

→ AskUserQuestion: 프로젝트?
   User: 대화 기반

→ AskUserQuestion: 출력 경로?
   User: 기본 경로

→ Task: worklog-writer (날짜 범위 선택 SKIP)
   프로젝트 경로: 대화 기반
   프로젝트 이름: general
   출력 경로: ~/Documents/docs/daily_work/
   추가 컨텍스트: 오늘 회의 내용 정리
```

**Example 5: Custom date range**
```
User: /worklog

→ AskUserQuestion: 날짜 범위?
   User: Other → "2025-01-01 ~ 2025-01-03"

→ Task: worklog-writer
   날짜 범위: 2025-01-01 ~ 2025-01-03
   패딩 범위: 2024-12-31 ~ 2025-01-04
```
