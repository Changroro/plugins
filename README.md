# changroro plugins

**문서 작성부터 커밋, 채용 지원, 프로젝트 이관까지. 반복하는 작업을 에이전트에게 맡깁니다.**

[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Plugins](https://img.shields.io/badge/Plugins-8-green?style=flat-square)](#플러그인)

창로로의 개인 워크플로를 모은 Claude Code 플러그인 마켓플레이스입니다. 각 플러그인은 작업 순서, 확인할 근거, 결과물 형식을 스킬과 명령으로 제공합니다. Codex에서도 사용하는 스킬이 있으며, 필요한 도구와 지원 범위는 개별 문서에서 확인할 수 있습니다.

## 빠른 시작

Claude Code에서 마켓플레이스를 등록하고 필요한 플러그인만 설치합니다.

```text
/plugin marketplace add Changroro/plugins
/plugin install docs@changroro
/docs:readme
```

다른 플러그인은 설치 명령의 `docs`를 아래 표의 이름으로 바꾸면 됩니다.

## 플러그인

플러그인 이름은 별도 저장소가 있을 때 해당 저장소로 연결됩니다. README 열에서 각 플러그인의 설치·사용 문서를 확인할 수 있습니다.

| 플러그인 | 맡길 수 있는 작업 | README |
|---|---|---|
| **docs** | 블로그·일지·포트폴리오·README, 세션 인계, 터미널 녹화 | [README](plugins/docs/README.md) |
| **gitwf** | Conventional Commits 커밋, PR 생성·리뷰 대응·병합 | [README](plugins/gitwf/README.md) |
| **jobs** | 공고 분석, 기업 리서치, 자소서 작성·퇴고, 면접 준비 | [README](plugins/jobs/README.md) |
| **ios** | Xcode MCP로 빌드·테스트·디버그, 기기 검증, App Store 배포 | [README](plugins/ios/README.md) |
| **project-rename** | mv-session 세션 이동 · mv-project 프로젝트·세션 전체 이관 | [README](plugins/project-rename/README.md) |
| [**find-me**](https://github.com/Changroro/find-me) | 개인 프롬프트로 대화 속 자기 발견과 맥락 기록 | [README](https://github.com/Changroro/find-me/blob/main/README.md) |
| [**imhuman**](https://github.com/Changroro/imhuman) | 내용을 유지하면서 한글의 AI 문체 탐지·윤문 | [README](https://github.com/Changroro/imhuman/blob/main/README.md) |
| [**code-video**](https://github.com/Changroro/code-video) | 주제를 조사하고 디자인에 맞춰 코드로 MP4 홍보 영상 제작 | [README](https://github.com/Changroro/code-video/blob/main/README.md) |

## 사용 방식

```text
작업 요청 → 스킬·명령 선택 → 근거 확인과 필요한 승인 → 결과물·검증
```

Claude Code에서는 `/플러그인:이름`, Codex에 설치한 스킬은 `$플러그인:이름`으로 호출합니다. Claude 전용 명령·hooks의 Codex 지원 여부는 개별 문서와 설치 환경을 확인하세요.

## 필요한 환경

| 작업 | 필요한 도구·환경 |
|---|---|
| 기본 사용 | Claude Code와 플러그인 설치 기능 |
| GitHub PR | Git, GitHub CLI(`gh`), 저장소 접근 인증 |
| 터미널 영상 | VHS, ttyd, ffmpeg |
| iOS 개발 | 스킬이 지정한 macOS·Xcode 환경, Xcode MCP, SimSlim, 배포 시 `asc` |
| 프로젝트·세션 이관 | Linux, `uv`, Python 3.11; Codex 이관 시 실제 상태 DB 경로 |

플러그인 설치와 외부 도구·계정 인증 준비는 별도 단계입니다. 자세한 조건은 각 플러그인 문서에 있습니다.

## 업데이트

Claude Code에서 카탈로그와 설치한 플러그인을 갱신합니다.

```text
/plugin marketplace update changroro
/plugin update docs@changroro
```

버전의 기준은 각 플러그인의 `.claude-plugin/plugin.json`입니다. 카탈로그에는 버전을 중복 기록하지 않습니다.

## 저장소 구성과 개발

| 경로 | 역할 |
|---|---|
| [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) | 로컬·외부 플러그인 카탈로그 |
| [plugins/](plugins) | 이 저장소에서 개발하는 플러그인 본체 |
| `plugins/<name>/README.md` | 각 플러그인의 설치·사용 문서 |
| [tests/](tests) | 스크립트와 문서 워크플로 검증 |

로컬 플러그인은 `plugins/<name>`에서 수정하고 해당 `plugin.json`의 버전을 올립니다. 별도 저장소의 플러그인은 그 저장소에서 수정·배포합니다. 카탈로그와 설명은 실제 구현을 기준으로 유지합니다.

## 라이선스

이 저장소는 [MIT License](LICENSE)를 따릅니다. 외부 플러그인의 라이선스·사용 조건은 각 저장소에서 확인하세요.
