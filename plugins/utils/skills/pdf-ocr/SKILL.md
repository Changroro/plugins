---
name: pdf-ocr
description: "PDF를 Claude vision으로 OCR하여 마크다운 변환. Use when user wants to extract text from PDF, convert PDF to markdown, OCR PDF, read scanned document, or process PDF with custom instructions. Supports custom prompts for tailored output."
---

# PDF OCR

PDF 파일을 Claude의 vision 기능으로 읽어 마크다운으로 변환합니다.

## Quick Start

```bash
# 기본 사용
/pdf-ocr /path/to/document.pdf

# 커스텀 지침과 함께
/pdf-ocr /path/to/document.pdf "표만 추출해줘"
```

## Core Workflow

### 1. PDF 경로 확인

사용자가 제공한 PDF 경로가 유효한지 확인합니다.

```bash
# 파일 존재 확인
ls -la <pdf_path>
```

### 2. PDF 읽기 (Vision 활용)

Claude의 Read 도구를 사용하여 PDF를 읽습니다. Read 도구는 PDF를 페이지별로 처리하며, 텍스트와 시각적 콘텐츠를 모두 분석합니다.

```
Read tool → PDF 파일 경로
```

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
- **NEVER** PDF 라이브러리(PyPDF, pdfplumber 등) 사용하지 않음
- **NEVER** 읽을 수 없는 부분을 추측으로 채우지 않음 (불명확시 [불명확] 표시)
