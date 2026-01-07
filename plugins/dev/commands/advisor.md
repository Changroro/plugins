---
description: Launch product-advisor agent for strategic project analysis
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

# Product Advisor Flow

## Pre-check: Read Current Directory

```bash
# Get current directory
pwd
```

Store these values:
- `{current_directory}`: Current working directory
- `{current_project_name}`: basename of current directory

## Step 1: Select Mode (분석 모드)

Use AskUserQuestion:

```
Question: "프로젝트 분석을 어떤 방식으로 진행할까요?"
Header: "분석 모드"
Options:
  - label: "자동 분석 (권장)", description: "프로젝트를 분석하여 자동으로 기획안 생성"
  - label: "토의 모드", description: "질의응답을 통해 함께 기획안 작성"
multiSelect: false
```

**NOTE**:
- 자동 분석: 프로젝트 구조, 코드, 설정 파일 등을 분석하여 자동으로 기획안 생성
- 토의 모드: 단계별 질문을 통해 사용자 의견을 반영하며 기획안 작성

## Step 2: Launch Agent

After collecting mode selection, use the Task tool with subagent_type='product-advisor':

**Prompt format for agent:**
```
프로젝트 경로: [current_directory]
프로젝트 이름: [current_project_name]
분석 모드: [auto 또는 interactive]
추가 컨텍스트: $ARGUMENTS
```

## Examples

**Auto mode:**
```
User: /advisor

→ AskUserQuestion: 분석 모드?
   User: 자동 분석

→ Task: product-advisor
   프로젝트 경로: /home/user/my-project
   프로젝트 이름: my-project
   분석 모드: auto
```

**Interactive mode:**
```
User: /advisor

→ AskUserQuestion: 분석 모드?
   User: 토의 모드

→ Task: product-advisor
   프로젝트 경로: /home/user/my-project
   프로젝트 이름: my-project
   분석 모드: interactive
```

**With context:**
```
User: /advisor 인증 기능 중심으로 분석해줘

→ AskUserQuestion: 분석 모드?
   User: 자동 분석

→ Task: product-advisor
   프로젝트 경로: /home/user/my-project
   프로젝트 이름: my-project
   분석 모드: auto
   추가 컨텍스트: 인증 기능 중심으로 분석해줘
```
