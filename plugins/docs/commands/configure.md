---
description: Configure docs plugin settings (base path, folder names for each document type)
allowed-tools:
  - Read
  - Write
  - Bash(mkdir:*)
  - Bash(cat:*)
  - Bash(pwd:*)
---

# Docs Configuration

Configure the docs plugin settings using AskUserQuestion to collect preferences interactively.

## Pre-check: Read Current Configuration

Before asking questions, check if config exists:

```bash
# Check current config
cat ~/.config/claude-code/docs_config.json 2>/dev/null || echo "NO_CONFIG"

# Get current directory
pwd
```

Store these values:
- `{current_config}`: Parsed config object or null
- `{current_directory}`: Current working directory

## Step 1: Select What to Configure (설정 항목 선택)

**IMPORTANT**: Use AskUserQuestion with `multiSelect: true` to let user choose which settings to configure.

```
Question: "어떤 항목을 설정하시겠습니까? (복수 선택 가능)"
Header: "설정 항목"
Options:
  - label: "기본 경로", description: "문서 저장 위치 설정"
  - label: "폴더명", description: "문서 타입별 폴더명 설정 (업무일지, 개발일지, 포트폴리오, 블로그, 코테)"
  - label: "블로그 말투", description: "블로그 글 작성 시 사용할 말투 스타일"
multiSelect: true
```

**NOTE**:
- 사용자가 선택한 항목만 이후 단계에서 질문합니다
- 선택하지 않은 항목은 기존 설정 유지 (설정이 없으면 기본값 사용)

---

## Step 2: Configure Selected Items Only

**선택한 항목에 해당하는 질문만 진행합니다.**

### 2-A. Base Path (기본 경로 선택 시)

Use AskUserQuestion:

```
Question: "문서를 저장할 기본 경로를 설정해주세요 (Other로 직접 입력 가능)"
Header: "기본 경로"
Options:
  - label: "{current_config.base_path 또는 ~/Documents/docs}", description: "현재 설정된 경로 유지"
  - label: "{current_directory}", description: "현재 작업 디렉토리 사용"
multiSelect: false
```

### 2-B. Folder Names (폴더명 선택 시)

먼저 프리셋 또는 개별 설정 선택:

```
Question: "폴더명을 어떻게 설정할까요?"
Header: "폴더 설정"
Options:
  - label: "기본값", description: "daily_work, daily_work_details, portfolio, blog, cote"
  - label: "간결하게", description: "work, dev, portfolio, blog, cote"
  - label: "개별 설정", description: "각 폴더명을 하나씩 직접 선택"
multiSelect: false
```

**If "개별 설정" selected**, ask each type:

#### Worklog folder (업무일지)
```
Question: "업무일지 폴더명을 선택해주세요"
Header: "업무일지"
Options:
  - label: "daily_work", description: "기본값 - 명확한 네이밍"
  - label: "work", description: "간결한 네이밍"
multiSelect: false
```

#### Devlog folder (개발일지)
```
Question: "개발일지 폴더명을 선택해주세요"
Header: "개발일지"
Options:
  - label: "daily_work_details", description: "기본값 - 업무일지와 연관성 표현"
  - label: "dev", description: "개발자 친화적 네이밍"
multiSelect: false
```

#### Portfolio folder
```
Question: "포트폴리오 폴더명을 선택해주세요"
Header: "포트폴리오"
Options:
  - label: "portfolio", description: "기본값 - 직관적인 이름"
  - label: "projects", description: "프로젝트 중심 네이밍"
multiSelect: false
```

#### Blog folder
```
Question: "블로그 폴더명을 선택해주세요"
Header: "블로그"
Options:
  - label: "blog", description: "기본값 - 간결한 이름"
  - label: "posts", description: "블로그 포스트 중심 네이밍"
multiSelect: false
```

#### Cote folder (코딩테스트)
```
Question: "코딩테스트 풀이 폴더명을 선택해주세요"
Header: "코테"
Options:
  - label: "cote", description: "기본값 - 코딩테스트 약자"
  - label: "algorithm", description: "알고리즘 중심 네이밍"
  - label: "boj", description: "백준 온라인 저지 약자"
multiSelect: false
```

### 2-C. Blog Writing Style (블로그 말투 선택 시)

```
Question: "블로그 글 작성 시 사용할 말투 스타일을 설정해주세요"
Header: "말투 스타일"
Options:
  - label: "기본 스타일", description: "플러그인 내장 기본 말투 사용"
  - label: "커스텀 파일", description: "Other로 직접 프롬프트 파일 경로 입력"
multiSelect: false
```

**NOTE**:
- "기본 스타일": 플러그인에 내장된 `assets/blog-style-default.md` 사용
- "커스텀 파일" 또는 Other: 사용자 정의 프롬프트 파일의 절대 경로 입력
  - 예: `~/Documents/my-blog-style.md`

## Step 3: Save Configuration

**IMPORTANT**: Merge selected settings with existing config. Only update fields that user chose to configure.

**Config file location**: `~/.config/claude-code/docs_config.json`

**Merge logic**:
1. Read existing config (or use defaults if none exists)
2. Update only the fields that user selected in Step 1
3. Write merged config back to file

**Default config (used when no existing config)**:
```json
{
  "base_path": "~/Documents/docs",
  "folders": {
    "worklog": "daily_work",
    "devlog": "daily_work_details",
    "portfolio": "portfolio",
    "blog": "blog",
    "cote": "cote"
  },
  "blog_style_prompt": "default",
  "path_structure": "{base}/{type}/{project}/"
}
```

## Step 4: Confirm and Display

After saving, display what was changed:

```
✅ Docs 설정이 저장되었습니다!

📝 변경된 항목:
  - 기본 경로: /path/to/docs (변경됨 or 기존 유지됨 표시)
  - 폴더명: work, dev, portfolio, blog (변경 시에만 표시)
  - 블로그 말투: default (변경 시에만 표시)

📁 현재 전체 설정:
  - 기본 경로: {base_path}
  - 업무일지: {folders.worklog}
  - 개발일지: {folders.devlog}
  - 포트폴리오: {folders.portfolio}
  - 블로그: {folders.blog}
  - 코테: {folders.cote}
  - 블로그 말투: {blog_style_prompt}

설정 파일: ~/.config/claude-code/docs_config.json
```

## Implementation

Use Bash tool to:
1. Create config directory if not exists: `mkdir -p ~/.config/claude-code`
2. Read existing config (if exists)
3. Merge with new settings
4. Write config file using Write tool

## Examples

**Example 1: Only change base path**
```
User: /docs:configure

→ Pre-check: 현재 설정 읽기, pwd 확인
→ AskUserQuestion (multiSelect): 어떤 항목을 설정하시겠습니까?
   User selects: [기본 경로] ✓

→ AskUserQuestion: 기본 경로?
   User: Other → "/home/user/my-docs"

→ Merge: base_path만 업데이트, 나머지는 기존 설정 유지
→ Save & Display
```

**Example 2: Change folders only**
```
User: /docs:configure

→ Pre-check: 현재 설정 읽기, pwd 확인
→ AskUserQuestion (multiSelect): 어떤 항목을 설정하시겠습니까?
   User selects: [폴더명] ✓

→ AskUserQuestion: 폴더명 설정 방식?
   User: "간결하게"

→ Merge: folders만 업데이트 (work, dev, portfolio, blog)
→ Save & Display
```

**Example 3: Configure multiple items**
```
User: /docs:configure

→ Pre-check: 현재 설정 읽기, pwd 확인
→ AskUserQuestion (multiSelect): 어떤 항목을 설정하시겠습니까?
   User selects: [기본 경로, 블로그 말투] ✓✓

→ AskUserQuestion: 기본 경로?
   User: 현재 디렉토리 사용

→ AskUserQuestion: 블로그 말투?
   User: Other → "~/my-prompts/casual-style.md"

→ Merge: base_path, blog_style_prompt만 업데이트
→ Save & Display
```
