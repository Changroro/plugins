---
name: pdf-ocr
description: "PDF를 Claude vision으로 OCR하여 마크다운 변환. MUST use this skill when user: (1) asks to convert PDF to markdown, (2) asks to OCR PDF, (3) sends PDF file and asks to extract/read/변환/추출, (4) mentions 'PDF 변환', 'PDF 읽어', 'PDF 마크다운'. This skill uses Task agent to protect main context from large PDF content - NEVER process PDF directly in main context."
context: fork
agent: general-purpose
---

# PDF OCR

PDF 파일을 Claude의 vision 기능으로 읽어 마크다운으로 변환합니다.

## Quick Start

```bash
# 단일 파일
/pdf-ocr /path/to/document.pdf

# 커스텀 지침과 함께
/pdf-ocr /path/to/document.pdf "표만 추출해줘"

# 폴더 내 모든 PDF (병렬 처리)
/pdf-ocr /path/to/folder/
```

## Core Workflow

### Step 1: 경로 타입 확인

```bash
# 파일인지 폴더인지 확인
ls -la <path>
```

**분기 처리:**
- **단일 파일** (.pdf) → [Single File Mode](#single-file-mode)로 진행
- **폴더** → [Batch Mode](#batch-mode-폴더-처리)로 진행

---

## Single File Mode

단일 PDF 파일 처리 워크플로우.

**IMPORTANT**: 단일 파일도 Task 에이전트를 사용하여 메인 컨텍스트를 보호합니다.

```
Task(subagent_type="general-purpose"):
  프롬프트: |
    PDF 파일을 OCR하여 마크다운으로 변환하고 저장해주세요.

    파일: [PDF 절대경로]
    커스텀 지침: [사용자 지침 있으면 포함]

    **수행 작업:**
    1. Read 도구로 PDF 읽기
    2. 마크다운으로 변환
    3. Write 도구로 [파일명].md 파일 저장
    4. 저장 완료 확인

    **에러 핸들링:**
    - 413 에러: "⚠️ 파일 크기 초과 (413 에러)"
    - 기타 에러: "⚠️ [에러 메시지]"

    **반환 형식 (내용 제외, 상태만):**
    ✅ 성공: [파일명] → [출력파일명].md
    또는
    ⚠️ 실패: [파일명] - [사유]
```

### 마크다운 변환 가이드라인

PDF 내용을 분석하여 다음 형식으로 마크다운 변환:

```markdown
# 문서 제목

## 섹션 1
본문 내용...

### 표
| 열1 | 열2 |
|-----|-----|
| 값  | 값  |

### 이미지/다이어그램 설명
[이미지 설명: ...]
```

### 4. 커스텀 지침 적용

사용자가 추가 지침을 제공한 경우:
- "표만 추출" → 표 형식 데이터만 마크다운 테이블로
- "요약해줘" → 핵심 내용만 요약
- "영어로 번역" → 번역된 결과물
- "코드만 추출" → 코드 블록만 추출

---

## Batch Mode (폴더 처리)

폴더 내 여러 PDF를 병렬로 처리.

### 1. PDF 파일 목록 수집

```bash
# 폴더 내 PDF 파일 목록
ls <folder_path>/*.pdf
```

### 2. 배치 분할 (3개 단위)

PDF 파일들을 **3개씩 그룹**으로 나눕니다:
- 그룹 1: file1.pdf, file2.pdf, file3.pdf
- 그룹 2: file4.pdf, file5.pdf, file6.pdf
- ...

### 3. 병렬 에이전트 실행

각 그룹에 대해 **Task 도구**로 병렬 에이전트 실행:

```
Task(subagent_type="general-purpose"):
  프롬프트: |
    다음 PDF 파일들을 OCR하여 마크다운으로 변환해주세요.

    파일 목록:
    - [file1.pdf 절대경로]
    - [file2.pdf 절대경로]
    - [file3.pdf 절대경로]

    커스텀 지침: [사용자 지침 있으면 포함]
    출력 폴더: [원본과 동일 폴더]

    **CRITICAL - 각 파일에 대해 에이전트 내에서 완료:**
    1. Read 도구로 PDF 읽기
    2. 에러 발생 시 skip하고 다음 파일로 (413 에러 등)
    3. 마크다운으로 변환
    4. **Write 도구로 [파일명].md 파일 저장** (반드시 에이전트 내에서!)
    5. 저장 완료 확인

    **IMPORTANT**:
    - 변환된 마크다운 내용을 메인으로 반환하지 마세요
    - 파일 저장까지 에이전트 내에서 완료해야 합니다
    - 메인에는 처리 결과 상태만 반환합니다

    처리 결과를 다음 형식으로만 보고 (내용 제외):
    ✅ 성공: [파일명] → [출력파일명].md
    ⚠️ SKIP: [파일명] - [사유]
```

**IMPORTANT**:
- 모든 그룹의 Task를 **동시에** 호출하여 병렬 실행
- 에이전트는 **Read + Write 모두 완료** 후 상태만 반환
- 메인 컨텍스트에 PDF 내용이 로드되지 않도록 함

### 4. 결과 집계

모든 에이전트 완료 후 결과 집계:

```markdown
## 📊 PDF OCR 처리 결과

### ✅ 성공 ([N]개)
- document1.pdf → document1.md
- document2.pdf → document2.md

### ⚠️ Skip ([M]개)
- large_file.pdf - 파일 크기 초과 (413 에러)
- corrupted.pdf - 읽기 실패

### 📁 출력 위치
[folder_path]/
```

---

## Output Format

### 기본 출력

```markdown
# [문서 제목]

> OCR 결과 - [페이지 수]p

## 내용

[변환된 마크다운 내용]

---
*Source: [파일명]*
```

### 저장 옵션

사용자가 요청시 결과를 파일로 저장:

```bash
# 같은 디렉토리에 .md 파일로 저장
/path/to/document.pdf → /path/to/document.md
```

## Supported Content Types

| 콘텐츠 | 변환 방식 |
|--------|-----------|
| 일반 텍스트 | 그대로 마크다운 |
| 제목/섹션 | # 헤딩으로 구조화 |
| 표 | 마크다운 테이블 |
| 목록 | - 또는 1. 형식 |
| 이미지/다이어그램 | [이미지 설명] 형태로 기술 |
| 코드 | ```언어``` 코드 블록 |
| 수식 | LaTeX ($...$) 형식 |

## Important Rules

### Context 보호 (핵심)
- **ALWAYS** Task 에이전트 내에서 Read + Write 모두 완료
- **ALWAYS** 에이전트는 처리 상태만 반환 (변환된 내용 반환 금지)
- **NEVER** 메인 컨텍스트에 PDF 내용을 로드하지 않음

### 처리 방식
- **ALWAYS** Read 도구를 사용하여 PDF 읽기 (라이브러리 사용 금지)
- **ALWAYS** 원본 문서의 구조를 최대한 보존
- **ALWAYS** 사용자 커스텀 지침이 있으면 우선 적용
- **ALWAYS** 에러 발생 시 해당 파일 skip하고 나머지 계속 처리
- **ALWAYS** 폴더 처리 시 3개 단위로 병렬 에이전트 실행
- **NEVER** PDF 라이브러리(PyPDF, pdfplumber 등) 사용하지 않음
- **NEVER** 읽을 수 없는 부분을 추측으로 채우지 않음 (불명확시 [불명확] 표시)
- **NEVER** 하나의 context에서 모든 PDF를 처리하지 않음 (메모리 초과 방지)
