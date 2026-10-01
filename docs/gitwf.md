# gitwf

**변경을 작업 단위로 커밋하고, PR 생성부터 리뷰 대응과 병합까지 이어갑니다.**

[마켓플레이스](../README.md) · [플러그인 소스](../plugins/gitwf)

## 소개

Git과 GitHub 작업을 위한 스킬 모음입니다. 변경 diff와 저장소 규칙을 읽고 커밋 메시지·PR 설명을 작성하며, 병합 전 테스트·CI·리뷰 상태를 확인합니다.

## 설치와 첫 사용

Claude Code에서 설치한 뒤 작업 중인 저장소에서 호출합니다.

```text
/plugin marketplace add Changroro/plugins
/plugin install gitwf@changroro
/gitwf:git-commit
이번 요청에 해당하는 변경만 한 커밋으로 저장해줘.
```

GitHub 작업에는 `gh`와 인증이 필요합니다.

```bash
git --version
gh --version
gh auth status
```

## 커밋과 PR 스킬

| 스킬 | 하는 일 |
|---|---|
| [git-commit](../plugins/gitwf/skills/git-commit/SKILL.md) | 작업 범위와 diff 확인, Emoji + Conventional Commits 메시지 작성 |
| [github-pr-creation](../plugins/gitwf/skills/github-pr-creation/SKILL.md) | 커밋·검증 결과에 근거한 제목·설명·라벨 구성과 PR 생성 |
| [github-pr-review](../plugins/gitwf/skills/github-pr-review/SKILL.md) | 리뷰 코멘트 수집·분류, 수정과 답변 처리 |
| [github-pr-merge](../plugins/gitwf/skills/github-pr-merge/SKILL.md) | 테스트·CI·리뷰 확인, 사용자 확인 뒤 병합과 후속 정리 |

Claude에서는 `/gitwf:github-pr-creation`, Codex에 설치한 스킬은 `$gitwf:github-pr-creation`처럼 호출합니다.

## 메시지 형식

```text
✨ feat(auth): 로그인 기능 추가
🐛 fix(api): 빈 응답 처리 수정
📝 docs(readme): 설치 예시 갱신
```

형식은 `emoji type(scope): subject`입니다. 커밋 작성자는 현재 저장소에 적용되는 Git 사용자 설정을 따릅니다. 기본 작업 단위는 사용자 요청 하나이며 관련 없는 변경을 함께 묶지 않습니다.

## 작동 방식

```text
작업 트리·diff 확인 → 범위 선택 → 테스트·리뷰 확인 → 커밋 또는 PR 작업
```

PR 작업은 GitHub CLI를 사용합니다. 브랜치·PR 대상·테스트 명령은 실제 프로젝트에서 확인합니다. 모든 저장소에 공통으로 적용되는 테스트 명령을 제공하는 것은 아닙니다.

## 필요한 도구와 지원 범위

Git 저장소 접근 권한과, PR 작업 시 GitHub CLI 인증·해당 저장소 권한이 필요합니다. 병합은 사용자 확인을 거칩니다. Claude용 데스크톱 알림 hooks가 포함되며 Codex의 hooks 지원은 별도로 확인해야 합니다.

## 라이선스

[MIT License](../LICENSE).
