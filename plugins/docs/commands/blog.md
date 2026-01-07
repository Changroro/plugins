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

## Step 1: Collect Topic (주제) - REQUIRED

주제는 **반드시** 입력받아야 합니다.

- If $ARGUMENTS contains a topic → Use it directly
- If $ARGUMENTS is empty → Ask user to input topic (사용자가 직접 입력)

**Do NOT use AskUserQuestion for topic** - just prompt the user to type it.

## Step 2: Collect Reference URLs (참고 URL) - OPTIONAL

Use AskUserQuestion:

```
Question: "참고할 URL이 있나요? (여러 개는 Other에서 쉼표로 구분)"
Header: "참고 URL"
Options:
  - label: "없음 (웹 검색으로 진행)", description: "URL 없이 자동으로 관련 자료 검색"
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
  - label: "~한다/~된다 체 (권장)", description: "자연스럽고 친근한 기술 블로그 스타일"
  - label: "~입니다/~습니다 체", description: "격식있고 정중한 스타일"
  - label: "~해요/~이에요 체", description: "친근하고 부드러운 스타일"
multiSelect: false
```

## Step 5: Select Output Path (저장 경로)

Use AskUserQuestion:

```
Question: "블로그 글을 어디에 저장할까요?"
Header: "저장 경로"
Options:
  - label: "기본 경로 (권장)", description: "docs/blog/{블로그제목}/ 폴더"
  - label: "현재 프로젝트 기반", description: "현재 프로젝트의 docs/blog/{블로그제목}/ 폴더"
multiSelect: false
```

**Default Path Structure**: `docs/blog/{blog_title}/blog_{date}.md`

## Step 6: Launch Agent

After collecting all inputs, use the Task tool with subagent_type='blog-writer':

**Prompt format for agent:**
```
주제: [collected_topic]
참고 URL: [collected_urls or "웹 검색"]
형식: [collected_format]
말투: [collected_style]
저장 경로: [collected_path]
블로그 제목: [sanitized blog title for folder name]

사용자가 직접 입력한 말투 설명: [if custom style was provided via Other]
사용자가 직접 입력한 경로: [if custom path was provided via Other]
```

**Path Resolution:**
- "기본 경로" → `docs/blog/{blog_title}/`
- "현재 프로젝트 기반" → `{current_project}/docs/blog/{blog_title}/`
- Custom (via Other) → User's specified path

## Quick Mode

If user provides all arguments inline, skip the interactive collection:
- Example: "/blog MCP 프로토콜 https://example.com markdown ~한다체"

In this case, parse the arguments and proceed directly to agent launch.

## Examples

**Interactive mode:**
```
User: /blog
Assistant: "어떤 주제로 블로그 글을 작성할까요? 주제를 입력해주세요."
User: "Docker 컨테이너 기초"
→ AskUserQuestion: 참고 URL?
→ AskUserQuestion: 형식?
→ AskUserQuestion: 말투?
→ AskUserQuestion: 저장 경로?
→ Task: blog-writer with collected inputs
```

**Quick mode:**
```
User: /blog Docker 입문 https://docs.docker.com
→ Task: blog-writer (주제: Docker 입문, URL: https://docs.docker.com, 형식: markdown, 말투: ~한다체, 경로: docs/blog/Docker-입문/)
```
