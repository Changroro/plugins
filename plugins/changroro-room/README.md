# changroro-room

**데스크톱 앱 대화 뒤에 흑백 도트 책상을 깔아 줍니다. 창로로가 노트북을 치고, 그 옆에 지금 세션의 상태와 오늘 할 일이 떠 있습니다.**

[마켓플레이스](../../README.md) · [플러그인 소스](.)

Claude Code [mods](https://code.claude.com/docs/en/plugins/mods/)로 만든 플러그인입니다. 배경과 색은 Claude Code 2.1.324 이상의 데스크톱·모바일 앱에서만 그려집니다. 터미널에서는 할 일 도구만 쓸 수 있습니다.

## 설치

```text
/plugin marketplace add Changroro/plugins
/plugin install changroro-room@changroro
```

설치한 뒤 새 Code 세션을 열면 적용됩니다. 사이드바를 접으면 왼쪽 그림이 다 보입니다.

## 화면

| 위치 | 그림 | 보여주는 것 |
|---|---|---|
| 왼쪽 위 | 도트 시계 | 현재 시각 (KST) |
| 왼쪽 | 배터리 | 컨텍스트 사용률, 80% 이상이면 빨간색 |
| 왼쪽 | 커피잔 | 프롬프트 캐시 남은 분, 식으면 "식었어요" |
| 왼쪽 아래 | 책상과 명패 | 창로로, 현재 저장소나 폴더 이름 |
| 오른쪽 | 보드 | 오늘 할 일과 완료 수 |
| 바닥 | 미니미 둘 | 답변이 끝나면 점프 |

색은 Ink & Paper 디자인 토큰을 따라 라이트 모드로 고정합니다.

## 오늘 할 일

"오늘 할 일은 A, B, C야"라고 말하면 Claude가 `todo` 도구로 적은 문장 그대로 등록하고, "B 끝났어"라고 하면 체크합니다. 목록은 세션이 바뀌어도 남고, KST 날짜가 바뀌면 비워집니다.

## 한계

- 캐시 시간은 답변이 끝난 시각부터 1시간 TTL로 셉니다. 5분 캐시 세션에서는 맞지 않습니다.
- 시계 때문에 1분마다 배경을 다시 그리며, 그때 미니미가 출발 위치로 돌아갑니다.

## 개발

도트 부품은 `scene/scene.py`에서 만듭니다. 고친 뒤 `python3 scene/scene.py`로 `hooks/parts.ts`를 다시 만들고, `claude plugin test .`와 `claude plugin validate .`로 확인합니다.
