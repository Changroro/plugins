# Git/GitHub 워크플로우 지침

## Git 작업 시 스킬 사용 필수

Git 관련 작업을 수행하기 전에 **반드시** 사용 가능한 스킬이 있는지 확인하고, 있다면 해당 스킬을 사용하세요.

### 사용 가능한 스킬 목록

| 작업 | 스킬 | 트리거 키워드 |
|------|------|---------------|
| 커밋 생성 | `gitwf:git-commit` | 커밋, commit, 커밋할까요 |
| PR 생성 | `gitwf:github-pr-creation` | PR 생성, pull request, PR 만들기 |
| PR 리뷰 코멘트 처리 | `gitwf:github-pr-review` | 리뷰 코멘트, PR 피드백, review comments |
| PR 병합 | `gitwf:github-pr-merge` | PR 머지, PR 병합, merge PR |

### 중요 규칙

1. **커밋 전**: `gitwf:git-commit` 스킬 사용 (Conventional Commits 형식 자동 적용)
2. **PR 생성 전**: `gitwf:github-pr-creation` 스킬 사용
3. **PR 리뷰 코멘트 해결 시**: `gitwf:github-pr-review` 스킬 사용
4. **PR 병합 시**: `gitwf:github-pr-merge` 스킬 사용

스킬을 사용하면 일관된 형식과 자동화된 워크플로우가 적용됩니다.
