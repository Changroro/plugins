# attention-ko

ADHD 친화 한국어 출력 스타일입니다. [attention-span](https://github.com/alexgreensh/attention-span)의 Attention-kind 스타일을 한국어로 옮기고, 긴 작업 중 진행 멘트가 영어로 새는 문제를 막는 규칙을 더했습니다.

## 설치

```text
/plugin marketplace add Changroro/plugins
/plugin install attention-ko@changroro
```

`/config`의 Output style에서 `attention-ko:Attention-kind`를 고르거나 `~/.claude/settings.json`에 직접 넣습니다. 새 세션부터 적용됩니다.

```json
"outputStyle": "attention-ko:Attention-kind"
```

## 원본과 다른 점

| 항목 | 원본 | attention-ko |
|---|---|---|
| 본문 언어 | 영어 | 한국어 |
| 쉬운 말 규칙 | Plain English | 쉬운 한국어, 번역투 금지 |
| 출력 언어 | 지정 없음 | 진행 멘트·질문·보고·compact 직후까지 한국어 고정 |
| 용어 | 지정 없음 | 내부 이름은 사람 말로 풀고, 조어 대신 표준 용어 |
| 질문 대응 | 질문은 한 번에 하나 | 번호 질문엔 같은 번호로 전부 답하고, 확인 안 된 답은 다음 답에서 다시 알림 |
| 근거 | 지정 없음 | 확인한 것과 추측을 나눠 표시 |
| 표 | 되도록 피함 | 비교·현황은 표로 |
| 포함 범위 | 스타일 3종, 스킬, 벤치마크 | Attention-kind 스타일 하나 |

## 라이선스

원본을 따라 [AGPL-3.0](LICENSE)입니다. 저장소의 MIT 라이선스는 이 폴더에 적용되지 않습니다. 원저작자와 수정 내역은 [NOTICE](NOTICE)에 있습니다.
