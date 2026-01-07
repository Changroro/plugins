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
- `{current_config_path}`: From config file or "미설정"
- `{current_directory}`: Current working directory

## Step 1: Base Path (기본 경로)

Use AskUserQuestion:

```
Question: "문서를 저장할 기본 경로를 설정해주세요 (Other로 직접 입력 가능)"
Header: "기본 경로"
Options:
  - label: "{current_config_path}", description: "현재 설정된 경로 유지"
  - label: "{current_directory}", description: "현재 작업 디렉토리 사용"
multiSelect: false
```

**NOTE**:
- 첫번째 옵션은 현재 설정 파일에 저장된 경로 (없으면 "~/Documents/docs")
- 두번째 옵션은 현재 pwd 결과

## Step 2: Document Type Folder Names

Use AskUserQuestion:

```
Question: "각 문서 타입별 폴더명을 설정할까요?"
Header: "폴더 설정"
Options:
  - label: "기본값 유지", description: "daily_work, daily_work_details, portfolio, blog"
  - label: "영문 간결하게", description: "work, dev, portfolio, blog"
multiSelect: false
```

If user selects via Other (커스텀), ask for each type:

### 2-1. Worklog folder (업무일지)
```
Question: "업무일지 폴더명을 선택해주세요"
Header: "업무일지"
Options:
  - label: "daily_work", description: "기본값 - 명확한 네이밍"
  - label: "work", description: "추천 - 간결한 네이밍"
multiSelect: false
```

### 2-2. Devlog folder (개발일지)
```
Question: "개발일지 폴더명을 선택해주세요"
Header: "개발일지"
Options:
  - label: "daily_work_details", description: "기본값 - 업무일지와 연관성 표현"
  - label: "dev", description: "추천 - 개발자 친화적 네이밍"
multiSelect: false
```

### 2-3. Portfolio folder
```
Question: "포트폴리오 폴더명을 선택해주세요"
Header: "포트폴리오"
Options:
  - label: "portfolio", description: "기본값 - 직관적인 이름"
  - label: "projects", description: "추천 - 프로젝트 중심 네이밍"
multiSelect: false
```

### 2-4. Blog folder
```
Question: "블로그 폴더명을 선택해주세요"
Header: "블로그"
Options:
  - label: "blog", description: "기본값 - 간결한 이름"
  - label: "posts", description: "추천 - 블로그 포스트 중심 네이밍"
multiSelect: false
```

## Step 3: Save Configuration

Save the collected settings to `docs_config.json`:

**Config file location**: `~/.config/claude-code/docs_config.json`

**Config format**:
```json
{
  "base_path": "/path/to/your/docs",
  "folders": {
    "worklog": "daily_work",
    "devlog": "daily_work_details",
    "portfolio": "portfolio",
    "blog": "blog"
  },
  "path_structure": "{base}/{type}/{project}/"
}
```

## Step 4: Confirm and Display

After saving, display the configuration:

```
✅ Docs 설정이 저장되었습니다!

📁 기본 경로: /path/to/your/docs
📂 폴더 구조:
  - 업무일지: {base_path}/daily_work/{project_name}/
  - 개발일지: {base_path}/daily_work_details/{project_name}/
  - 포트폴리오: {base_path}/portfolio/{project_name}/
  - 블로그: {base_path}/blog/{project_name}/

설정 파일: ~/.config/claude-code/docs_config.json
```

## Implementation

Use Bash tool to:
1. Create config directory if not exists: `mkdir -p ~/.config/claude-code`
2. Write config file using Write tool
3. Verify the file was created successfully

## Examples

**First-time setup:**
```
User: /docs:configure

→ Pre-check: 현재 설정 읽기 (NO_CONFIG), pwd 확인
→ AskUserQuestion: 기본 경로?
   Options: [~/Documents/docs (미설정), /home/user/project (현재 디렉토리)]
   User: Other → "/home/user/Documents/dev-docs"

→ AskUserQuestion: 폴더 설정?
   User: 기본값 유지

→ Save to ~/.config/claude-code/docs_config.json
→ Display confirmation
```

**Custom folder names:**
```
User: /docs:configure

→ Pre-check: 현재 설정 읽기, pwd 확인
→ AskUserQuestion: 기본 경로?
   Options: [/home/user/docs (현재 설정), /home/user/project (현재 디렉토리)]
   User: 현재 설정 유지

→ AskUserQuestion: 폴더 설정?
   User: Other → 개별 설정

→ AskUserQuestion: 업무일지 폴더명?
   Options: [daily_work, work]
   User: Other → "worklog"

→ ... (각 타입별 질문)

→ Save config with custom folder names
```
