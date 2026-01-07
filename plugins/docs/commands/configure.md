---
description: Configure docs plugin settings (base path, folder names for each document type)
---

# Docs Configuration

Configure the docs plugin settings using AskUserQuestion to collect preferences interactively.

## Step 1: Base Path (기본 경로)

Use AskUserQuestion:

```
Question: "문서를 저장할 기본 경로를 설정해주세요"
Header: "기본 경로"
Options:
  - label: "홈 디렉토리", description: "~/Documents/docs 또는 유사한 경로"
  - label: "직접 입력", description: "원하는 경로 직접 지정"
multiSelect: false
```

## Step 2: Document Type Folder Names

Use AskUserQuestion:

```
Question: "각 문서 타입별 폴더명을 설정할까요? (기본값 사용 시 '기본값 유지' 선택)"
Header: "폴더 설정"
Options:
  - label: "기본값 유지 (권장)", description: "daily_work, daily_work_details, portfolio, blog"
  - label: "커스텀 설정", description: "각 폴더명을 직접 지정"
multiSelect: false
```

If user selects "커스텀 설정", ask for each type:

### 2-1. Worklog folder (업무일지)
```
Question: "업무일지 폴더명을 입력해주세요 (기본값: daily_work)"
Header: "업무일지"
Options:
  - label: "daily_work (기본값)", description: "기본 폴더명 사용"
  - label: "직접 입력", description: "다른 폴더명 사용"
multiSelect: false
```

### 2-2. Devlog folder (개발일지)
```
Question: "개발일지 폴더명을 입력해주세요 (기본값: daily_work_details)"
Header: "개발일지"
Options:
  - label: "daily_work_details (기본값)", description: "기본 폴더명 사용"
  - label: "직접 입력", description: "다른 폴더명 사용"
multiSelect: false
```

### 2-3. Portfolio folder
```
Question: "포트폴리오 폴더명을 입력해주세요 (기본값: portfolio)"
Header: "포트폴리오"
Options:
  - label: "portfolio (기본값)", description: "기본 폴더명 사용"
  - label: "직접 입력", description: "다른 폴더명 사용"
multiSelect: false
```

### 2-4. Blog folder
```
Question: "블로그 폴더명을 입력해주세요 (기본값: blog)"
Header: "블로그"
Options:
  - label: "blog (기본값)", description: "기본 폴더명 사용"
  - label: "직접 입력", description: "다른 폴더명 사용"
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

→ AskUserQuestion: 기본 경로?
   User: 직접 입력 → "/home/user/Documents/dev-docs"

→ AskUserQuestion: 폴더 설정?
   User: 기본값 유지

→ Save to ~/.config/claude-code/docs_config.json
→ Display confirmation
```

**Custom folder names:**
```
User: /docs:configure

→ AskUserQuestion: 기본 경로?
   User: 직접 입력 → "/home/user/docs"

→ AskUserQuestion: 폴더 설정?
   User: 커스텀 설정

→ AskUserQuestion: 업무일지 폴더명?
   User: 직접 입력 → "worklog"

→ ... (각 타입별 질문)

→ Save config with custom folder names
```
