# docs

**개발 기록을 블로그, 일지, 포트폴리오와 다음 세션의 인수인계 문서로 만듭니다.**

[마켓플레이스](../../README.md) · [플러그인 소스](.)

## 소개

문서마다 독자와 목적이 다릅니다. 업무 성과를 전달하는 업무일지, 구현 과정을 남기는 개발일지, 프로젝트를 설명하는 포트폴리오를 각각의 작성 흐름으로 제공합니다. README와 세션 인계, 터미널 영상도 같은 플러그인에서 요청할 수 있습니다.

## 설치와 첫 사용

Claude Code에서 실행합니다.

```text
/plugin marketplace add Changroro/plugins
/plugin install docs@changroro
/docs:readme
```

저장 위치·문서별 폴더명·블로그 말투는 `/docs:configure`로 설정합니다. 설정 파일은 `~/.config/claude-code/docs_config.json`입니다.

## 문서 작성

| 명령 | 결과물 |
|---|---|
| `/docs:blog` | 주제와 자료를 바탕으로 Tistory 스타일 글과 로컬 이미지 수집 |
| `/docs:worklog` | 업무 성과와 진행 상황을 전달하는 업무일지 |
| `/docs:devlog` | Git 변경과 구현 내용을 설명하는 개발일지 |
| `/docs:portfolio` | 프로젝트 목적·구현·성과를 정리한 포트폴리오 |
| `/docs:configure` | 저장 위치·폴더명·작성 설정 |

주제나 프로젝트, 출력 위치 등 필요한 입력을 수집한 뒤 전용 작성 에이전트에 전달합니다.

## README와 프로젝트 기억

| 스킬 | 역할 |
|---|---|
| [readme](skills/readme/SKILL.md) | 코드·설정에 근거한 설치·사용·기능 설명과 적합한 시각 자산 구성 |
| [handover](skills/handover/SKILL.md) | 이번 결과와 다음 작업을 HANDOFF에 정리하고 지식을 알맞은 문서에 배치 |
| [restart](skills/restart/SKILL.md) | 문서·코드·설정으로 프로젝트 기억을 다시 구성 |
| [terminal-gif-maker](skills/terminal-gif-maker/SKILL.md) | `.tape`로 재생성 가능한 터미널 GIF·MP4·WebM 제작 |

```text
/docs:handover
/docs:terminal-gif-maker
현재 CLI의 기본 사용 흐름을 README용 GIF로 녹화해줘.
```

`handover`는 세션 관련 내용만 갱신하고, `restart`는 프로젝트 기억을 전반적으로 재구성합니다. 제품·구현 지식은 프로젝트 문서에, 에이전트 작업 규칙은 근거와 독립 검토를 거쳐 AGENTS에 배치합니다.

## 작동 방식

```text
주제·프로젝트·출력 위치 → 코드·대화·자료 확인 → 문서 작성 → 검증
```

README는 프로젝트 유형에 맞춰 구성하고 실제 이미지가 있을 때 배너·스크린샷을 활용합니다. 터미널 영상은 VHS가 ttyd 터미널에서 `.tape`를 실행하고 ffmpeg으로 인코딩합니다.

## 필요한 도구와 지원 범위

기본 문서는 에이전트의 파일·Git·자료 읽기 도구를 사용합니다. 터미널 녹화에는 VHS, ttyd, ffmpeg이 필요하며, 배너 생성·문서 검증에는 해당 스크립트의 Python 의존성을 준비합니다.

Claude Code용 명령·작성 에이전트·알림 hooks를 포함합니다. Codex에서는 설치한 스킬을 `$docs:readme`, `$docs:handover`처럼 호출합니다. Claude 전용 명령·hooks는 런타임의 변환·지원 여부를 확인해야 합니다. 데스크톱 알림 hooks는 권한 요청·입력 대기·작업 완료를 전달합니다.

## 라이선스

[MIT License](../../LICENSE).
