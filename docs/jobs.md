# jobs

**공고를 읽고, 조사한 회사와 직무에 맞춰 자소서·면접 준비 자료를 만듭니다.**

[마켓플레이스](../README.md) · [플러그인 소스](../plugins/jobs)

## 소개

지원 회사별 폴더에서 공고·리서치·자기소개서를 함께 관리하는 채용 지원 플러그인입니다. 초기화부터 공고 분석·기업 조사·문항 작성·퇴고·면접 준비까지 단계별 스킬을 제공합니다.

## 설치와 첫 사용

Claude Code에서 설치한 뒤 지원 자료를 둘 디렉터리에서 실행합니다.

```text
/plugin marketplace add Changroro/plugins
/plugin install jobs@changroro
/jobs:init
```

공고를 전달하고 리서치를 이어갑니다.

```text
/jobs:crawl
이 채용공고를 분석해줘: <채용공고 URL>
/jobs:research
```

## 지원 워크플로

```text
init → crawl → research → write → review → interview
```

| 스킬 | 입력과 결과 |
|---|---|
| [init](../plugins/jobs/skills/init/SKILL.md) | 현재 디렉터리에 지원 폴더 구조와 기본 문서 생성 |
| [crawl](../plugins/jobs/skills/crawl/SKILL.md) | 공고 URL에서 요구사항을 추출해 `채용공고.md` 작성 |
| [research](../plugins/jobs/skills/research/SKILL.md) | 기업·직무와 자소서 자료를 병렬 조사해 `리서치/`에 정리 |
| [write](../plugins/jobs/skills/write/SKILL.md) | 문항 유형과 분량에 맞춰 자기소개서 초안 작성 |
| [review](../plugins/jobs/skills/review/SKILL.md) | 클리셰·일관성·표현·분량 검토와 퇴고 |
| [interview](../plugins/jobs/skills/interview/SKILL.md) | 1분 자기소개, 서류 기반 질문, 면접 시뮬레이션 준비 |

각 단계를 따로 요청할 수도 있습니다. Codex에 설치한 스킬은 `$jobs:write`, `$jobs:review`처럼 호출합니다. 초기화가 만드는 작업 지침은 Claude의 `TeamCreate` 팀 운영을 전제로 하므로, Codex에서는 해당 지침을 그대로 실행할 수 있는지 확인해야 합니다.

## 작성 자료와 템플릿

초기화는 `CLAUDE.local.md`, `채용공고.md`, `자기소개서.md`, `리서치/` 등 기본 구조를 만듭니다. 조사 자료와 문항·경험을 읽어 작성하므로 지원자의 실제 경험과 성과를 함께 제공해야 합니다.

[templates/](../plugins/jobs/templates)에는 지원동기·입사후포부·경험 소재·분량 전략·표현 개선·면접 질문 등의 자료가 있습니다. 문항에 맞는 템플릿을 선택하고 앞 단계의 자료를 다음 단계에서 활용합니다.

## 필요한 도구와 지원 범위

웹 검색·페이지 읽기·파일 작성이 가능한 에이전트 환경이 필요합니다. 접근 제한이 있는 공고는 실제로 읽을 수 있는 자료가 추가로 필요할 수 있습니다. 조사 출처와 실제 경험·수치·공고 요구사항을 제출 전에 검토하세요.

지원 문서 작성과 면접 준비를 돕는 플러그인입니다. 채용 사이트 계정 연결이나 지원서 자동 제출 기능은 포함하지 않습니다.

## 라이선스

[MIT License](../LICENSE).
