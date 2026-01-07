---
description: Launch readme-architect agent to create/improve README.md
allowed-tools:
  - Read
  - Write
  - Bash(git -C:*)
  - Bash(git config:*)
  - Bash(git log:*)
  - Bash(mkdir:*)
  - Bash(cat:*)
  - Bash(pwd:*)
  - Glob
  - Grep
  - AskUserQuestion
---

# README Creation Flow

## Pre-check: Read Current Directory

```bash
# Get current directory
pwd
```

Store these values:
- `{current_directory}`: Current working directory
- `{current_project_name}`: basename of current directory

## Step 1: Select Mode (작성 모드)

Use AskUserQuestion:

```
Question: "README를 어떤 방식으로 작성할까요?"
Header: "작성 모드"
Options:
  - label: "자동 모드 (권장)", description: "프로젝트를 분석하여 자동으로 README 생성"
  - label: "토의 모드", description: "질의응답을 통해 함께 README 작성"
multiSelect: false
```

**NOTE**:
- 자동 모드: 프로젝트 구조, 코드, package.json 등을 분석하여 자동 생성
- 토의 모드: 단계별 질문을 통해 사용자 의견을 반영하며 작성

## Step 2: Launch Agent

After collecting mode selection, use the Task tool with subagent_type='readme-architect':

**Prompt format for agent:**
```
프로젝트 경로: [current_directory]
프로젝트 이름: [current_project_name]
작성 모드: [auto 또는 interactive]
추가 컨텍스트: $ARGUMENTS
```

## Examples

**Auto mode:**
```
User: /readme

→ AskUserQuestion: 작성 모드?
   User: 자동 모드

→ Task: readme-architect
   프로젝트 경로: /home/user/my-project
   프로젝트 이름: my-project
   작성 모드: auto
```

**Interactive mode:**
```
User: /readme

→ AskUserQuestion: 작성 모드?
   User: 토의 모드

→ Task: readme-architect
   프로젝트 경로: /home/user/my-project
   프로젝트 이름: my-project
   작성 모드: interactive
```

**With context:**
```
User: /readme CLI 도구입니다

→ AskUserQuestion: 작성 모드?
   User: 자동 모드

→ Task: readme-architect
   프로젝트 경로: /home/user/cli-tool
   프로젝트 이름: cli-tool
   작성 모드: auto
   추가 컨텍스트: CLI 도구입니다
```
