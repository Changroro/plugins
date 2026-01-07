---
description: Launch portfolio-writer agent to create/update project portfolio with interactive input collection
allowed-tools:
  - Read
  - Write
  - Bash(git -C:*)
  - Bash(git config:*)
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(git diff:*)
  - Bash(mkdir:*)
  - Bash(cat:*)
  - Bash(pwd:*)
  - Glob
  - Grep
---

# Portfolio Creation Flow

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
Question: "어떤 프로젝트의 포트폴리오를 작성할까요?"
Header: "프로젝트"
Options:
  - label: "{current_directory}", description: "현재 디렉토리 프로젝트 분석하여 포트폴리오 생성"
  - label: "대화 기반", description: "특정 프로젝트 경로 없이 대화 내용으로 작성"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: 현재 pwd 결과 (해당 디렉토리의 코드, README, git 히스토리 분석)
- 두번째 옵션: 프로젝트 분석 없이 대화 내용 기반으로 작성
- Other: 사용자가 직접 프로젝트 경로 입력

## Step 2: Select Output Path (출력 경로)

Use AskUserQuestion:

```
Question: "포트폴리오를 어디에 저장할까요?"
Header: "출력 경로"
Options:
  - label: "{config_base_path}/portfolio/", description: "설정된 기본 경로 사용"
  - label: "{current_directory}/docs/portfolio/", description: "현재 프로젝트 내 docs 폴더"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: configure에서 설정한 경로 (없으면 ~/Documents/docs/portfolio/)
- 두번째 옵션: 현재 프로젝트 디렉토리의 docs/portfolio/
- Other: 사용자가 직접 경로 입력

## Step 3: Launch Agent

After collecting all inputs, use the Task tool with subagent_type='portfolio-writer':

**Prompt format for agent:**
```
프로젝트 경로: [selected_project_path or "대화 기반"]
프로젝트 이름: [project_name]
출력 경로: [selected_output_path]
추가 컨텍스트: $ARGUMENTS
```

**Path Resolution:**
- 프로젝트 경로가 지정된 경우 → 해당 경로에서 코드/README/git 분석
- "대화 기반" 선택 시 → 프로젝트 분석 없이 대화 내용으로 작성
- 출력 경로: `{output_path}/{project_name}/portfolio.md`
  - 예: `~/Documents/docs/portfolio/awesome-api/portfolio.md`

## Examples

**Current directory project:**
```
User: /portfolio

→ Pre-check: config 읽기, pwd 확인 (/home/user/awesome-api)
→ AskUserQuestion: 프로젝트?
   Options: [/home/user/awesome-api, 대화 기반]
   User: /home/user/awesome-api

→ AskUserQuestion: 출력 경로?
   Options: [~/Documents/docs/portfolio/, /home/user/awesome-api/docs/portfolio/]
   User: 설정된 기본 경로 사용

→ Task: portfolio-writer
   프로젝트 경로: /home/user/awesome-api
   프로젝트 이름: awesome-api
   출력 경로: ~/Documents/docs/portfolio/awesome-api/portfolio.md
```

**Different project path:**
```
User: /portfolio

→ AskUserQuestion: 프로젝트?
   User: Other → "/home/user/old-project"

→ AskUserQuestion: 출력 경로?
   User: 현재 프로젝트 내 docs 폴더

→ Task: portfolio-writer
   프로젝트 경로: /home/user/old-project
   프로젝트 이름: old-project
   출력 경로: /home/user/current/docs/portfolio/old-project/portfolio.md
```

**Conversation-based:**
```
User: /portfolio 사이드 프로젝트 정리

→ AskUserQuestion: 프로젝트?
   User: 대화 기반

→ AskUserQuestion: 출력 경로?
   User: 기본 경로

→ Task: portfolio-writer
   프로젝트 경로: 대화 기반
   프로젝트 이름: side-project
   출력 경로: ~/Documents/docs/portfolio/side-project/portfolio.md
   추가 컨텍스트: 사이드 프로젝트 정리
```
