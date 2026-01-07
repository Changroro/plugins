---
name: pdf-ocr
description: "PDF를 Claude vision으로 OCR하여 마크다운 변환. Use when user wants to extract text from PDF, convert PDF to markdown, OCR PDF, read scanned document, or process PDF with custom instructions. Supports custom prompts for tailored output."
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

### 1. PDF 읽기 (Vision 활용)

Claude의 Read 도구를 사용하여 PDF를 읽습니다. Read 도구는 PDF를 페이지별로 처리하며, 텍스트와 시각적 콘텐츠를 모두 분석합니다.

```
Read tool → PDF 파일 경로
```

### 2. 에러 핸들링

**413 에러 (Request too large) 발생 시:**
```
⚠️ SKIP: [파일명] - 파일 크기 초과 (413 에러)
```
- 해당 파일을 건너뛰고 다음 파일로 진행
- 최종 결과에 skip된 파일 목록 포함

**기타 API 에러 발생 시:**
```
⚠️ SKIP: [파일명] - [에러 메시지]
```
- 에러를 기록하고 나머지 파일 계속 처리

### 3. 마크다운 변환

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

    각 파일에 대해:
    1. Read 도구로 PDF 읽기
    2. 에러 발생 시 skip하고 다음 파일로 (413 에러 등)
    3. 마크다운으로 변환
    4. [파일명].md로 저장

    처리 결과를 다음 형식으로 보고:
    ✅ 성공: [파일명]
    ⚠️ SKIP: [파일명] - [사유]
```

**IMPORTANT**: 모든 그룹의 Task를 **동시에** 호출하여 병렬 실행

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

- **ALWAYS** Read 도구를 사용하여 PDF 읽기 (라이브러리 사용 금지)
- **ALWAYS** 원본 문서의 구조를 최대한 보존
- **ALWAYS** 사용자 커스텀 지침이 있으면 우선 적용
- **ALWAYS** 에러 발생 시 해당 파일 skip하고 나머지 계속 처리
- **ALWAYS** 폴더 처리 시 3개 단위로 병렬 에이전트 실행
- **NEVER** PDF 라이브러리(PyPDF, pdfplumber 등) 사용하지 않음
- **NEVER** 읽을 수 없는 부분을 추측으로 채우지 않음 (불명확시 [불명확] 표시)
- **NEVER** 하나의 context에서 모든 PDF를 처리하지 않음 (메모리 초과 방지)
