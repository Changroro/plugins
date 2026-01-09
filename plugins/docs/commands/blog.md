---
description: Launch blog-writer agent to create a technical blog post with interactive input collection
allowed-tools:
  - Read
  - Write
  - Bash(git *)
  - Bash(mkdir *)
  - Bash(cat *)
  - Bash(pwd)
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

First, check if a custom style prompt is configured:
```bash
# Check config for blog_style_prompt
cat ~/.config/claude-code/docs_config.json 2>/dev/null | grep -o '"blog_style_prompt"[^,}]*' || echo "NO_STYLE_CONFIG"
```

Store `{config_style_prompt}`: From config file or "default"

Use AskUserQuestion:

```
Question: "말투 스타일을 선택해주세요 (Other로 프롬프트 파일 경로, 참고 URL, 직접 설명 입력 가능)"
Header: "말투"
Options:
  - label: "기본 프롬프트 ({config_style_prompt})", description: "configure에서 설정한 말투 프롬프트 파일 사용 (기본: 창빵맨 스타일)"
  - label: "요약 스타일", description: "간결하고 핵심만 전달하는 문서형 스타일 (~이다 체)"
multiSelect: false
```

**NOTE - 선택지별 처리**:
- "기본 프롬프트": config의 `blog_style_prompt` 값 전달
  - `default` → `prompt_file:default`
  - 커스텀 경로 → `prompt_file:/path/to/file.md`
- "요약 스타일" → `style:summary`
- Other (직접 입력) → 입력값 그대로 전달 (agent가 해석)
  - 파일 경로 (~/로 시작하거나 /로 시작) → agent가 파일 읽기
  - URL (http로 시작) → agent가 URL 분석
  - 텍스트 → agent가 스타일 설명으로 해석

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
말투: [style_value - see below]
저장 경로: [collected_path]
블로그 제목: [sanitized blog title for filename]
```

**말투 값 형식 (agent가 해석)**:
- `prompt_file:default` → 플러그인 내장 기본 프롬프트 (agent가 읽음)
- `prompt_file:/path/to/file.md` → 해당 경로의 프롬프트 파일 (agent가 읽음)
- `style:summary` → 요약 스타일 (내장 규칙 적용)
- `~/my-style.md` 또는 `/path/to/style.md` → 파일 경로 (agent가 읽음)
- `https://example.com/blog` → URL (agent가 분석)
- 기타 텍스트 → 말투 설명 (agent가 해석)

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
