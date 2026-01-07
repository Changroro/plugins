---
description: Launch blog-writer agent to create a technical blog post with interactive input collection
allowedTools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
---

# Blog Post Creation Flow

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

## Step 1: Collect Topic (주제) - REQUIRED

주제는 **반드시** 입력받아야 합니다.

- If $ARGUMENTS contains a topic → Use it directly
- If $ARGUMENTS is empty → Use AskUserQuestion

Use AskUserQuestion:

```
Question: "어떤 주제로 블로그 글을 작성할까요?"
Header: "주제"
Options:
  - label: "{current_directory} 프로젝트 기반", description: "현재 디렉토리 프로젝트를 분석하여 블로그 주제 도출"
  - label: "대화 기반", description: "특정 프로젝트 없이 주제를 직접 입력 (Other 사용)"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: 현재 pwd 디렉토리의 프로젝트 분석하여 블로그 주제 자동 도출
- 두번째 옵션: Other로 직접 주제 입력 유도
- Other: 사용자가 원하는 주제 직접 입력

## Step 2: Collect Reference URLs (참고 URL) - OPTIONAL

Use AskUserQuestion:

```
Question: "참고할 URL이 있나요? (여러 개는 Other에서 쉼표로 구분)"
Header: "참고 URL"
Options:
  - label: "없음 (웹 검색으로 진행)", description: "URL 없이 자동으로 관련 자료 검색"
  - label: "프로젝트 README 참고", description: "현재 프로젝트의 README.md를 참고 자료로 활용"
multiSelect: false
```

## Step 3: Select Format (출력 형식)

Use AskUserQuestion:

```
Question: "어떤 형식으로 작성할까요?"
Header: "형식"
Options:
  - label: "Markdown (권장)", description: "GitHub, 대부분의 블로그 플랫폼 호환"
  - label: "HTML", description: "웹페이지 직접 삽입용"
multiSelect: false
```

## Step 4: Select Writing Style (말투)

Use AskUserQuestion:

```
Question: "어떤 말투로 작성할까요?"
Header: "말투"
Options:
  - label: "참고 URL 스타일", description: "참고 URL의 말투를 분석하여 유사하게 작성 (URL 필요)"
  - label: "기술블로그 스타일 (권장)", description: "~한다/~된다 체, 자연스럽고 친근한 개발자 블로그"
multiSelect: false
```

**NOTE**:
- "참고 URL 스타일" 선택 시: Step 2에서 URL을 제공했어야 함. URL의 말투를 분석하여 유사하지만 완전히 동일하지 않게 작성
- "기술블로그 스타일" 선택 시: 기본 ~한다/~된다 체로 작성

## Step 5: Select Output Path (저장 경로)

Use AskUserQuestion:

```
Question: "블로그 글을 어디에 저장할까요?"
Header: "저장 경로"
Options:
  - label: "{config_base_path}/blog/", description: "설정된 기본 경로 사용"
  - label: "{current_directory}/docs/blog/", description: "현재 프로젝트 내 docs/blog 폴더"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션: configure에서 설정한 경로 (없으면 ~/Documents/docs/blog/)
- 두번째 옵션: 현재 프로젝트 디렉토리의 docs/blog/
- Other: 사용자가 직접 경로 입력

**Output filename**: `{output_path}/{blog_title}_{YYYY-MM-DD}.md`

## Step 6: Launch Agent

After collecting all inputs, use the Task tool with subagent_type='blog-writer':

**Prompt format for agent:**
```
프로젝트 경로: [project_path if "프로젝트 기반" selected, or "대화 기반"]
주제: [collected_topic or "프로젝트 분석"]
참고 URL: [collected_urls or "웹 검색"]
형식: [collected_format]
말투: [collected_style]
저장 경로: [collected_path]
블로그 제목: [sanitized blog title for filename]

사용자가 직접 입력한 말투 설명: [if custom style was provided via Other]
사용자가 직접 입력한 경로: [if custom path was provided via Other]
```

**Path Resolution:**
- 설정된 기본 경로 → `{config_base_path}/blog/{blog_title}_{date}.md`
- 현재 프로젝트 내 → `{current_directory}/docs/blog/{blog_title}_{date}.md`
- Custom (via Other) → User's specified path

## Quick Mode

If user provides all arguments inline, skip the interactive collection:
- Example: "/blog MCP 프로토콜 https://example.com markdown ~한다체"

In this case, parse the arguments and proceed directly to agent launch.

## Examples

**Project-based blog:**
```
User: /blog

→ Pre-check: config 읽기, pwd 확인 (/home/user/awesome-api)
→ AskUserQuestion: 주제?
   Options: [/home/user/awesome-api 프로젝트 기반, 대화 기반]
   User: 프로젝트 기반

→ AskUserQuestion: 참고 URL?
   User: 프로젝트 README 참고

→ AskUserQuestion: 형식?
   User: Markdown

→ AskUserQuestion: 말투?
   User: 기술블로그 스타일

→ AskUserQuestion: 저장 경로?
   Options: [~/Documents/docs/blog/, /home/user/awesome-api/docs/blog/]
   User: 설정된 기본 경로

→ Task: blog-writer
   프로젝트 경로: /home/user/awesome-api
   주제: 프로젝트 분석
   저장 경로: ~/Documents/docs/blog/awesome-api-소개_2025-01-07.md
```

**Topic-based blog:**
```
User: /blog

→ AskUserQuestion: 주제?
   User: 대화 기반

→ AskUserQuestion: 주제를 입력해주세요 (대화 기반 선택 시)
   User: Other → "Docker 컨테이너 기초"

→ AskUserQuestion: 참고 URL?
   User: Other → "https://docs.docker.com"

→ AskUserQuestion: 형식?
→ AskUserQuestion: 말투?
→ AskUserQuestion: 저장 경로?

→ Task: blog-writer
   프로젝트 경로: 대화 기반
   주제: Docker 컨테이너 기초
   참고 URL: https://docs.docker.com
   저장 경로: ~/Documents/docs/blog/Docker-컨테이너-기초_2025-01-07.md
```

**Quick mode:**
```
User: /blog Docker 입문 https://docs.docker.com
→ Task: blog-writer (주제: Docker 입문, URL: https://docs.docker.com, 형식: markdown, 말투: 기술블로그 스타일, 경로: docs/blog/Docker-입문_2025-01-07.md)
```
