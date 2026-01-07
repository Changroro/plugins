---
description: Launch daily-work-writer agent to generate work logs with interactive input collection
allowedTools:
  - Read
  - Write
  - Bash
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

## Step 3: Launch Agent

After collecting all inputs, use the Task tool with subagent_type='worklog-writer':

**Prompt format for agent:**
```
프로젝트 경로: [selected_project_path or "대화 기반"]
프로젝트 이름: [project_name]
출력 경로: [selected_output_path]
추가 컨텍스트: $ARGUMENTS
```

**Path Resolution:**
- 프로젝트 경로가 지정된 경우 → 해당 경로에서 git log 분석
- "대화 기반" 선택 시 → git 분석 없이 대화 내용으로 작성
- 출력 파일명: `{output_path}/{project_name}_{YYYY-MM-DD}.md`

## Examples

**Current directory project:**
```
User: /worklog

→ Pre-check: config 읽기, pwd 확인 (/home/user/myproject)
→ AskUserQuestion: 프로젝트?
   Options: [/home/user/myproject, 대화 기반]
   User: /home/user/myproject

→ AskUserQuestion: 출력 경로?
   Options: [~/Documents/docs/daily_work/, /home/user/myproject/docs/daily_work/]
   User: ~/Documents/docs/daily_work/

→ Task: worklog-writer
   프로젝트 경로: /home/user/myproject
   프로젝트 이름: myproject
   출력 경로: ~/Documents/docs/daily_work/myproject_2025-01-07.md
```

**Conversation-based:**
```
User: /worklog 오늘 회의 내용 정리

→ AskUserQuestion: 프로젝트?
   User: 대화 기반

→ AskUserQuestion: 출력 경로?
   User: 기본 경로

→ Task: worklog-writer
   프로젝트 경로: 대화 기반
   프로젝트 이름: general
   출력 경로: ~/Documents/docs/daily_work/general_2025-01-07.md
   추가 컨텍스트: 오늘 회의 내용 정리
```
