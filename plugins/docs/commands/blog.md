---
description: Launch blog-writer agent to create a technical blog post with interactive input collection
allowed-tools:
  - Read
  - Write
  - Bash(git *)
  - Bash(mkdir *)
  - Bash(cat *)
  - Bash(pwd)
  - Bash(python *)
  - Bash(python3 *)
  - Glob
  - Grep
  - WebFetch
  - WebSearch
---

# Blog Post Creation Flow (Tistory 스타일 / 로컬 이미지 수집)

## Pre-check: Read Configuration and Current Directory

```bash
# Check current config for default path
cat ~/.config/claude-code/docs_config.json 2>/dev/null || echo "NO_CONFIG"

# Get current directory
pwd
```

Store these values:
- `{config_base_path}`: From config file or `docs`
- `{current_directory}`: Current working directory
- `{current_project_name}`: basename of current directory

---

## Step 1: Collect Topic (주제) - REQUIRED

주제는 **반드시** 입력받아야 합니다.

- If `$ARGUMENTS` contains a topic → Use it directly
- Otherwise → AskUserQuestion

```
Question: "어떤 주제로 블로그 글을 작성할까요?"
Header: "주제"
Options:
  - label: "{current_directory} 프로젝트 기반", description: "현재 디렉토리 프로젝트를 분석하여 블로그 주제 도출"
  - label: "대화 기반", description: "특정 프로젝트 없이 주제를 직접 입력 (Other 사용)"
multiSelect: false
```

---

## Step 2: Collect Reference URLs (참고 URL) - 다중 입력 지원

여러 개 입력하면 **쉼표**로 구분 (Other에서).

```
Question: "참고할 URL이 있나요? (여러 개는 Other에서 쉼표로 구분)"
Header: "참고 URL"
Options:
  - label: "없음 (웹 검색)", description: "URL 없이 자동으로 관련 자료 검색"
  - label: "프로젝트 README 참고", description: "현재 프로젝트의 README.md를 참고 자료로 활용"
  - label: "URL 입력 (단일 또는 다중)", description: "Other로 URL 입력. 여러 개는 쉼표로 구분"
multiSelect: false
```

agent에 전달할 때:
- `없음` → `웹 검색`
- `프로젝트 README 참고` → `프로젝트 README 참고`
- `URL 입력` Other 텍스트 → 그대로 전달 (agent가 쉼표로 split)

---

## Step 3: Select Format (출력 형식)

```
Question: "어떤 형식으로 작성할까요?"
Header: "형식"
Options:
  - label: "Markdown + inline HTML (티스토리 권장)", description: "단일 .md, 본문은 마크다운 + 허용된 inline HTML(img/strong/blockquote 등). 티스토리 에디터에 그대로 붙여넣기 가능."
  - label: "Markdown only", description: "순수 마크다운만. GitHub/일반 블로그 호환. HTML 태그 미사용."
multiSelect: false
```

> **note**: HTML 단독 파일(.html) 옵션은 제거되었습니다. 본문은 항상 .md입니다.
> 티스토리는 본문 내 `style="..."` 인라인 CSS를 제거하므로 agent는 CSS를 절대 출력하지 않습니다.

---

## Step 4: Select Writing Style (말투)

먼저 configure 설정 확인:

```bash
cat ~/.config/claude-code/docs_config.json 2>/dev/null | grep -o '"blog_style_prompt"[^,}]*' || echo "NO_STYLE_CONFIG"
```

Store `{config_style_prompt}`: From config file or `default`

```
Question: "말투 스타일을 선택해주세요 (Other로 프롬프트 파일 경로, 참고 URL, 직접 설명 입력 가능)"
Header: "말투"
Options:
  - label: "기본 프롬프트 ({config_style_prompt})", description: "configure 설정 말투 사용 (기본: Tistory 창빵맨 스타일)"
  - label: "요약 스타일", description: "간결하고 핵심만 전달하는 문서형 스타일 (~이다 체)"
multiSelect: false
```

**선택지별 처리**:
- `기본 프롬프트` → `prompt_file:default` 또는 `prompt_file:{custom_path}`
- `요약 스타일` → `style:summary`
- Other → 입력값 그대로 (파일 경로 / URL / 텍스트 — agent가 해석)

---

## Step 5: Image Mode (이미지 처리) — NEW

본문에 이미지를 어떻게 처리할지 선택합니다.

```
Question: "본문 이미지 처리 방식을 선택해주세요"
Header: "이미지 모드"
Options:
  - label: "auto — 자동 후보 제안 (권장)", description: "agent가 본문 작성 중 시각 자료 필요 지점을 식별하고 WebSearch/WebFetch로 후보를 찾아 사용자 확인 후 로컬 다운로드"
  - label: "manual — 직접 제공", description: "본문 작성 후 이미지 자리별로 사용자에게 URL/로컬 경로 요청"
  - label: "skip — 이미지 없음", description: "텍스트 + 코드 블록만으로 작성"
multiSelect: false
```

agent에 전달:
- `auto` → `이미지 모드: auto`
- `manual` → `이미지 모드: manual`
- `skip` → `이미지 모드: skip`

---

## Step 6: Select Output Path (저장 경로)

```
Question: "블로그 글을 어디에 저장할까요?"
Header: "저장 경로"
Options:
  - label: "{config_base_path}/blog/", description: "configure 설정된 기본 경로"
  - label: "{current_directory}/docs/blog/", description: "현재 프로젝트 내 docs/blog/"
multiSelect: false
```

**최종 파일명**: `{output_path}/{blog_title_slug}_{YYYY-MM-DD}.md`
**이미지 폴더**: `{output_path}/{blog_title_slug}-images/`
**메타 파일**: `{output_path}/{blog_title_slug}_{YYYY-MM-DD}.images.json`

---

## Step 7: Launch Agent

수집된 모든 입력을 모아 `blog-writer` agent에 Task 호출.

**Prompt format**:
```
프로젝트 경로: [project_path or "대화 기반"]
주제: [topic or "프로젝트 분석"]
참고 URL: [collected_urls or "웹 검색" or "프로젝트 README 참고"]
형식: [Markdown + inline HTML | Markdown only]
말투: [style_value — prompt_file:.../style:summary/경로/URL/텍스트]
저장 경로: [output_path]
블로그 제목: [sanitized blog title]
이미지 모드: [auto | manual | skip]
이미지 폴더: [output_path]/[slug]-images
```

---

## Quick Mode

사용자가 인자를 인라인으로 모두 제공하면 Q&A 생략:
```
/blog MCP 프로토콜 https://example.com auto
```
파싱 후 바로 agent 호출.

---

## 발행 안내 (사용자에게 출력 후 항상 안내)

블로그 글 작성이 끝나면 다음 메시지를 사용자에게 표시:

> **티스토리 발행 가이드**
>
> 1. 생성된 `.md` 파일 본문을 티스토리 글쓰기 (마크다운 모드)에 붙여넣기.
> 2. 본문 안의 `<img src="./{slug}-images/img-NN.png">` 자리에, 티스토리 에디터의 **본문 이미지 첨부** 기능으로 같은 파일을 다시 업로드.
>    - 티스토리 자체 CDN(`t1.daumcdn.net`)이 영구 호스팅합니다.
> 3. 로컬 이미지 폴더 (`{slug}-images/`) 와 `.images.json` 은 GitHub 미러링 / 로컬 미리보기 / 추후 재발행용으로 보관.
> 4. 환경변수 설정 불필요 (R2 등 외부 스토리지 사용 안 함).

---

## Examples

### Example 1: 프로젝트 기반 + auto 이미지
```
User: /blog

→ Pre-check: config 읽기, pwd = /home/user/awesome-api
→ AskUserQuestion: 주제 → "프로젝트 기반"
→ AskUserQuestion: 참고 URL → "프로젝트 README 참고"
→ AskUserQuestion: 형식 → "Markdown + inline HTML"
→ AskUserQuestion: 말투 → "기본 프롬프트"
→ AskUserQuestion: 이미지 모드 → "auto"
→ AskUserQuestion: 저장 경로 → "현재 디렉토리/docs/blog/"

→ Task: blog-writer
   프로젝트 경로: /home/user/awesome-api
   주제: 프로젝트 분석
   참고 URL: 프로젝트 README 참고
   형식: Markdown + inline HTML
   말투: prompt_file:default
   저장 경로: /home/user/awesome-api/docs/blog/
   블로그 제목: awesome-api-소개
   이미지 모드: auto
   이미지 폴더: /home/user/awesome-api/docs/blog/awesome-api-소개-images
```

### Example 2: 주제 직접 + 다중 URL + manual 이미지
```
User: /blog

→ 주제 → Other: "Docker 컨테이너 기초"
→ 참고 URL → Other: "https://docs.docker.com, https://github.com/docker/docker"
→ 형식 → "Markdown + inline HTML"
→ 말투 → "기본 프롬프트"
→ 이미지 모드 → "manual"
→ 저장 경로 → "기본 경로"

→ Task: blog-writer
   프로젝트 경로: 대화 기반
   주제: Docker 컨테이너 기초
   참고 URL: https://docs.docker.com, https://github.com/docker/docker
   형식: Markdown + inline HTML
   말투: prompt_file:default
   저장 경로: ~/Documents/docs/blog/
   블로그 제목: Docker-컨테이너-기초
   이미지 모드: manual
   이미지 폴더: ~/Documents/docs/blog/Docker-컨테이너-기초-images
```

### Example 3: skip 이미지 + 요약 스타일
```
User: /blog

→ 주제 → Other: "uv vs pip 비교"
→ 참고 URL → "웹 검색"
→ 형식 → "Markdown only"
→ 말투 → "요약 스타일"
→ 이미지 모드 → "skip"
→ 저장 경로 → "기본 경로"

→ Task: blog-writer (이미지 단계 자체 생략)
```

### Example 4: Quick Mode
```
User: /blog "Docker 입문" https://docs.docker.com auto

→ Parse: topic=Docker 입문, url=https://docs.docker.com, image_mode=auto
→ Defaults: format=Markdown + inline HTML, style=prompt_file:default, path=설정 기본
→ Task: blog-writer (Q&A 생략)
```
