---
name: geeknews-news
description: "GeekNews(news.hada.io) 뉴스 수집. GeekNews 새 글을 확인하고 싶을 때 사용."
---

# GeekNews 수집 스킬

## 실행 절차

### 1단계: 스크립트 실행

```bash
python3 {SKILL_DIR}/scripts/geeknews_collector.py 2>/dev/null
```

- 출력이 있으면 새 글이 있는 것. 출력이 비어있으면 새 글 없음.
- 중복 제거는 스크립트가 자동 처리.

### 2단계: 결과 전달

- 출력이 **비어있으면** → 어떤 메시지도 보내지 마라. 완전히 침묵.
- 출력이 있으면 → `GeekNews 새 글` 헤더와 함께 전달.

전송 형식:
- `[제목](URL)` 형식 유지. URL을 절대 제거하지 마라.
- 스크립트 출력 데이터만 사용. 데이터를 지어내지 마라.

## 금지 사항

- 브라우저를 사용하지 마라.
- 스크립트 출력에 없는 데이터를 만들어내지 마라.
- 사용자에게 질문하지 마라.
