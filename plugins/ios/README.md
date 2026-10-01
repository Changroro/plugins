# ios

**Xcode의 빌드·테스트·디버그 도구를 에이전트에 연결하고 기기 검증과 App Store 배포까지 진행합니다.**

[마켓플레이스](../../README.md) · [플러그인 소스](.)

## 소개

네이티브 iOS·Swift 프로젝트를 위한 `ios-dev` 스킬입니다. 개발 작업은 Xcode MCP 브리지, 시뮬레이터 관리는 Device Hub와 SimSlim, 배포는 `asc` CLI로 연결합니다.

## 필요한 환경

| 용도 | 스킬이 요구하는 환경 |
|---|---|
| 개발 | Apple Silicon, macOS 26.6+, Xcode 27+ |
| 에이전트 연결 | Xcode Settings → Intelligence → Model Context Protocol → Xcode Tools 활성화 |
| 시뮬레이터 | Device Hub, SimSlim과 프로젝트별 프로필 |
| 실기기 | 기기 연결·Developer Mode, 사용자가 연 iPhone Mirroring |
| 배포 | `asc`, App Store Connect 인증, 서명·프로비저닝 환경 |

이 표는 [현재 스킬의 실행 조건](skills/ios-dev/SKILL.md)입니다.

## 설치와 Xcode 연결

Claude Code에서 설치합니다.

```text
/plugin marketplace add Changroro/plugins
/plugin install ios@changroro
```

프로젝트 디렉터리에서 브리지를 확인하고 등록합니다.

```bash
xcrun --find mcpbridge
claude mcp add -s project xcode -- xcrun mcpbridge
```

Codex는 `codex mcp add xcode -- xcrun mcpbridge`로 등록합니다. Claude의 프로젝트 스코프와 달리 Codex 등록은 전역 설정에 반영됩니다.

```text
/ios:ios-dev
현재 프로젝트를 빌드하고 테스트 실패 원인을 확인해줘.
```

Codex에 설치한 스킬 호출은 `$ios:ios-dev`입니다.

## 개발과 검증

| 단계 | 처리 내용 |
|---|---|
| 빌드·테스트 | Xcode 도구로 빌드, XCTest·Swift Testing 실행, 진단 확인 |
| 디버그 | 스킴·대상·빌드 설정 확인, 디버거와 콘솔 사용 |
| UI 확인 | SwiftUI preview 또는 기기 도구의 스크린샷·계층 확인 |
| 시뮬레이터 | Device Hub 관리, `simslim verify`로 프로필과 차이 확인 |
| 실기기 | 사용자 승인 뒤 설치·실행, iPhone Mirroring과 콘솔로 검증 |

```text
Xcode MCP 연결 → 빌드·테스트·디버그 → 시뮬레이터·실기기 검증 → 배포
```

일반 개발 흐름은 Xcode MCP를 사용합니다. 스크립트·CI 경로 또는 설명된 브리지 부재 상황의 `xcodebuild` 사용 조건은 스킬을 따릅니다.

## App Store 배포

```bash
brew install asc
asc auth status
asc doctor
```

인증은 사용자가 직접 준비합니다. `asc`로 archive·export 후 TestFlight 업로드 또는 App Store 심사 제출을 진행합니다. 심사 제출 전 앱·버전·빌드·릴리스 노트를 제시하고 확인받으며 게시한 빌드는 태그와 사용자용 변경 기록을 남깁니다.

## 지원 범위

macOS의 네이티브 iOS 환경을 대상으로 합니다. 실기기 설치·실행, 시뮬레이터 데이터 영구 삭제, App Store 제출은 각각 승인 절차가 있습니다. 사이드로드·크로스플랫폼 전환은 별도의 선택입니다.

## 라이선스

[MIT License](../../LICENSE).
