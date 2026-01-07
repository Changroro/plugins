# TODO

## 완료된 이슈
- [x] 업무일지/개발일지 작성 시 git commit 작성자 구분 기능 추가
- [x] 블로그 글 작성 시 AskUserQuestion 기반 단계별 입력 수집 기능 추가
- [x] docs 플러그인 경로 구조 일관화 및 설정 기능 추가

## 진행 상황

### 이슈 1: Git Commit 작성자 구분
- [x] Git Commit Analysis 섹션에 author 구분 로직 추가
- [x] Work Log Format Structure에 "내 작업 내용" / "팀원 작업 내용" 별도 섹션 추가
- [x] Writing Guidelines에 각 섹션별 작성 가이드라인 추가
- [x] Edge Cases 섹션 추가 (커밋 없음, 본인만, 팀원만)
- [x] Error Handling에 git user 미설정 케이스 추가

### 이슈 2: 블로그 글 작성 Interactive Input
- [x] blog.md command에 AskUserQuestion 기반 5단계 입력 수집 추가
  - Step 1: 주제 (필수)
  - Step 2: 참고 URL (선택적)
  - Step 3: 형식 (기본값: Markdown)
  - Step 4: 말투 (기본값: ~한다/~된다 체)
  - Step 5: 저장 경로 (기본경로/현재프로젝트/직접입력)
- [x] blog-writer.md agent가 수집된 입력을 파싱하도록 수정
- [x] 사용자 커스텀 말투 입력 시 규칙 추출하여 일관되게 적용하는 로직 추가

### 이슈 3: Docs 경로 구조 일관화
- [x] 모든 docs agent에 일관된 경로 구조 적용: `{base}/{type}/{project}/`
- [x] docs:configure command 생성 (기본 경로, 폴더명 설정)
- [x] docs_config.json 설정 파일 지원 추가
- [x] 경로 옵션 일관화: 기본 경로 / 현재 프로젝트 / 직접 입력

## 메모

### Git Commit 작성자 구분
- `git config user.name` / `git config user.email`로 현재 사용자 식별
- `git log --format="%H|%an|%ae|%ad|%s"`로 author 정보 포함하여 조회
- author가 현재 사용자와 일치하면 "내 작업", 아니면 "팀원 작업"으로 분류

### 블로그 Interactive Input
- Command 레벨에서 AskUserQuestion으로 입력 수집 → Agent에게 전달
- Agent가 백그라운드에서 돌아가므로, 입력 수집은 Command에서 처리
- 커스텀 말투 입력 시: 패턴 분석 → 규칙 생성 → 일관 적용

### Docs 경로 구조
- 경로 구조: `{base_path}/{type_folder}/{project_name}/filename.md`
- 설정 파일 위치:
  1. `{project}/.claude/docs_config.json` (프로젝트 레벨)
  2. `~/.config/claude-code/docs_config.json` (글로벌)
- 폴더명 기본값: daily_work, daily_work_details, portfolio, blog
- `/docs:configure`로 설정 변경 가능
