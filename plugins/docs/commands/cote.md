---
description: 백준 풀이 .py 파일을 분석하여 문제 정리 마크다운을 생성한다. 디렉토리 내 .py 파일이 여러 개면 배치/단일 선택을 묻고, 배치 선택 시 파일별 에이전트를 병렬 실행한다.
allowed-tools:
  - Read
  - Write
  - Bash(cat *)
  - Bash(pwd)
  - Bash(ls *)
  - Bash(mkdir *)
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
---

# 코딩테스트 문제 정리 커맨드

이 커맨드는 현재 디렉토리의 `.py` 파일을 탐색하고, 각 파일에서 백준 문제 URL과 풀이 코드를 추출한 뒤, cote-writer 에이전트를 실행하여 구조화된 문제 정리 마크다운을 생성한다.

파일이 여러 개일 경우 사용자에게 배치(전체) 또는 단일(최신) 처리를 선택받고, 배치 선택 시 파일별 에이전트를 병렬로 실행한다.

---

## 실행 흐름

```
config 읽기 → .py 파일 전체 탐색 → 파일 수에 따라 분기
  1개: 바로 에이전트 실행
  N개: AskUserQuestion → "전체 파일" 또는 "최신 파일만"
    → 전체: 각 파일 URL 검증 → N개 에이전트 병렬 실행 → 요약 리포트
    → 최신: 최신 파일 1개만 에이전트 실행
```

---

## Step 1: 설정 및 환경 읽기

```bash
cat ~/.config/claude-code/docs_config.json 2>/dev/null || echo "NO_CONFIG"
pwd
```

| 변수 | 값 |
|------|-----|
| `{config}` | 파싱된 config 또는 기본값 |
| `{current_directory}` | 현재 작업 디렉토리 |
| `{base_path}` | config.base_path 또는 `~/Documents/docs` |
| `{cote_folder}` | config.folders.cote 또는 `cote` |
| `{cote_template}` | config.cote_template 또는 `default` |

## Step 2: .py 파일 전체 탐색

현재 디렉토리의 모든 `.py` 파일을 수정 시간순으로 조회한다.

```bash
ls -t *.py 2>/dev/null
```

결과가 없으면 `py/` 하위 디렉토리를 시도한다:
```bash
ls -t py/*.py 2>/dev/null
```

- `{all_py_files}`: 발견된 전체 .py 파일 목록 (최신순)
- `{py_file_count}`: 파일 개수
- 파일이 0개면 → `"현재 디렉토리에서 .py 파일을 찾을 수 없습니다."` 출력 후 종료

## Step 3: 처리 모드 결정

**파일이 1개**: 질문 없이 해당 파일로 바로 진행한다.

**파일이 2개 이상**: 반드시 AskUserQuestion으로 사용자에게 묻는다.

```
Question: "{py_file_count}개의 .py 파일을 발견했습니다. 어떻게 처리할까요?"
Header: "처리 모드"
Options:
  - label: "전체 파일", description: "발견된 {py_file_count}개 파일 모두 정리 (병렬 실행)"
  - label: "최신 파일만", description: "{newest_file} 파일만 정리"
multiSelect: false
```

- "전체 파일" 선택 → `{target_files}` = 전체 파일 목록
- "최신 파일만" 선택 → `{target_files}` = 최신 파일 1개

## Step 4: 파일별 URL 및 코드 추출

`{target_files}`의 각 파일을 읽어 정보를 추출한다:

1. 파일 첫 줄에서 백준 URL 추출: `# https://www.acmicpc.net/problem/{number}`
2. 나머지 부분에서 사용자 풀이 코드 추출
3. URL이 없는 파일은 스킵 목록에 추가하고 경고 출력

파일별 저장값:
- `{py_file_path}`: 파일 경로
- `{problem_url}`: 백준 URL
- `{problem_number}`: 문제 번호
- `{user_code}`: URL 주석을 제외한 풀이 코드

## Step 5: 저장 경로 결정

| 조건 | 경로 |
|------|------|
| config에 base_path + folders.cote 있음 | `{base_path}/{cote_folder}/` |
| 그 외 | `{current_directory}/docs/cote/` |

## Step 6: 에이전트 실행

URL 검증을 통과한 각 파일에 대해 Task tool로 cote-writer 에이전트를 실행한다.

**에이전트 프롬프트 형식:**
```
py 파일 경로: {py_file_path}
문제 URL: {problem_url}
내 코드:
{user_code}
저장 경로: {output_path}
템플릿: {cote_template}
```

**단일 모드**: Task 1개 실행.

**배치 모드**: 파일 수만큼 Task를 **한 번의 응답에서 병렬로** 실행한다. devlog 커맨드의 병렬 Task 패턴과 동일하다.

배치 예시 (3개 파일):
```
Task 1: subagent_type='docs:cote-writer', prompt="py 파일 경로: .../17609.py\n문제 URL: .../17609\n..."
Task 2: subagent_type='docs:cote-writer', prompt="py 파일 경로: .../1234.py\n문제 URL: .../1234\n..."
Task 3: subagent_type='docs:cote-writer', prompt="py 파일 경로: .../5678.py\n문제 URL: .../5678\n..."
→ 3개를 한 번의 응답에서 동시에 호출
```

## Step 7: 결과 리포트

배치 모드일 경우 모든 에이전트 완료 후 요약을 출력한다:

```
코딩테스트 문제 정리가 완료되었습니다.

처리 결과:
- ✅ 17609번 회문 → ~/Documents/docs/cote/17609_회문.md
- ✅ 1234번 정렬 → ~/Documents/docs/cote/1234_정렬.md
- ⚠️ solution.py: URL 없음 (스킵)

총 2/3개 파일 처리 완료
저장 위치: ~/Documents/docs/cote/
```

단일 모드일 경우 에이전트가 자체 리포트를 출력하므로 추가 리포트 불필요.

---

## 에러 처리

| 상황 | 대응 |
|------|------|
| .py 파일 없음 | `"현재 디렉토리에서 .py 파일을 찾을 수 없습니다."` |
| URL 주석 없음 (단일 모드) | `"py 파일 첫 줄에 백준 문제 URL을 # 주석으로 추가해주세요."` |
| URL 주석 없음 (배치 모드) | 해당 파일 스킵, 요약에서 경고 표시 |
