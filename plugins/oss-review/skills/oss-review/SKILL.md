---
name: oss-review
description: "사용자가 자신이 개발한 프로젝트·레포·오픈소스를 출시·공개·릴리즈·배포 전에 전체적으로 점검·검수·리뷰받고 싶어 할 때 사용하는 종합 리뷰 스킬. 라이센스(참고한 레포 라이센스의 README/LICENSE 반영 포함), 전체 코드리뷰(Claude Opus 4.7와 Codex GPT-5.5 교차 2인 병렬), 보안 취약점, 데드코드·레거시·사일런트 fallback, UI/UX(다크·라이트·모바일 화면을 Playwright로 점검)의 5개 영역을 각각 새 컨텍스트 서브에이전트로 병렬 점검하고 하나의 통합 보고서를 만든 뒤 승인을 받아 수정한다. 다음과 같은 경우 'oss-review'라고 명시하지 않더라도 반드시 이 스킬을 사용할 것: '내 프로젝트/레포/오픈소스 리뷰해줘·점검해줘·검수해줘', '공개 전 점검', '출시 전 검수', '릴리즈 전 검토', '깃헙에 올리기 전 점검', '배포 전 검수', 'v1.0/태그 달기 전 코드리뷰', 'codex랑 claude 둘 다 써서 코드리뷰'; 그리고 코드·보안·라이센스·UI·데드코드 중 둘 이상을 함께 봐달라거나, 출시·공개 준비가 됐는지 다각도로 판단해 달라는 요청. 단일 PR 한 건 리뷰나 한 가지 측면만 점검하는 요청에는 code-review·security-review 등 전용 도구를 쓴다."
---

# oss-review: 오픈소스 프로젝트 종합 리뷰

사용자가 개발한 오픈소스 프로젝트를 출시/공개 전 마지막으로 점검하기 위한 멀티-에이전트 리뷰 파이프라인이다. 매 호출마다 **컨텍스트가 비어 있는 새로운 서브에이전트**들을 5개 카테고리에 걸쳐 병렬 실행하고, 결과를 **하나의 통합 보고서**로 사용자에게 제시한 뒤, **사용자 승인 후에만 수정 작업**으로 진입한다.

이 스킬은 **Claude(Opus 4.7)** 와 **Codex(GPT-5.5)** 두 호스트에서 모두 사용할 수 있게 작성되어 있다. Claude Code에서 호출되면 `Agent` 도구로 서브에이전트를 spawn하고, Codex CLI에서 호출되면 동등한 서브에이전트 메커니즘(Codex의 task 분기 기능)을 사용한다. 본문에서 "서브에이전트"라고 표현하는 모든 자리는 **호스트 환경의 동등 도구로 매핑된다**.

## 핵심 원칙 (반드시 준수)

1. **매번 새 컨텍스트**: 직전 세션에서 사용한 에이전트를 재사용하지 않는다. 매 실행마다 호스트의 서브에이전트 도구로 **새로운** 인스턴스를 spawn한다. 이전 대화 맥락이 결과를 오염시키지 않게 하기 위함이다.
2. **모델: 호스트 최상위 모델 고정**: 모든 서브에이전트는 호스트의 최상위 모델로 호출한다.
   - **Claude 호스트**: 반드시 **Claude Opus 4.7 (`claude-opus-4-7`)**. `Agent` 도구 호출 시 `model: "opus"` 별칭을 지정한다 — 현재 이 환경에서 `opus` 별칭은 Claude Opus 4.7로 해석된다. 별칭이 다른 버전(예: 4.8)을 가리키도록 바뀐 경우 본 스킬은 즉시 업데이트되어야 한다.
   - **Codex 호스트**: 반드시 **GPT-5.5 (`gpt-5.5`)**. 그 미만 모델로 다운그레이드 금지.
   - 어느 호스트든 절대 Sonnet/Haiku/하위 버전으로 다운그레이드하지 않는다. 비용보다 결과 품질이 중요한 단계다.
   - 추가 안전장치: 모든 서브에이전트 prompt 첫 줄에 호스트별 식별 문구를 박는다.
     - Claude 호출 시: `"당신은 Claude Opus 4.7 모델로 호출된 리뷰어입니다."`
     - Codex 호출 시: `"당신은 OpenAI Codex / GPT-5.5 모델로 호출된 리뷰어입니다."`
3. **읽기 전용 분석**: 5개 서브에이전트는 분석/보고만 하고 **코드를 직접 수정하지 않는다**. 수정은 본 스킬(메인 컨텍스트)이 통합 보고서로 사용자에게 보고 → 승인 → 적용 순서로만 진행한다.
4. **승인 게이트**: 어떤 수정도 사용자가 명시적으로 "진행" "OK" "승인" 등의 의사를 표시하기 전에는 시작하지 않는다.
5. **간단한 작업은 직접 / 복잡한 작업은 워크트리 + 팀**: 승인 후 수정 단계에서 단일 파일 수준의 트리비얼 수정은 메인 컨텍스트에서 직접 처리하고, 다중 파일·구조 변경·아키텍처 수정 등은 `git worktree`를 새로 파고 팀을 소집해 격리된 브랜치에서 진행한다.
   - Claude 호스트에서는 `TeamCreate`로 팀 소집.
   - Codex 호스트에서는 Codex의 multi-task 기능 또는 별도 Codex 인스턴스를 worktree 안에서 가동.

---

## 호스트 감지 및 도구 매핑

스킬 시작 시 다음 신호로 호스트를 식별한다:

| 신호 | 호스트 |
|------|-------|
| `Agent`, `TaskCreate`, `Skill` 도구가 존재 | Claude Code |
| `codex --version` 또는 `~/.codex/AGENTS.md` 존재, Claude 도구 없음 | Codex CLI |

도구 매핑:

| 추상 작업 | Claude Code | Codex CLI |
|----------|-------------|-----------|
| 새 컨텍스트 서브에이전트 spawn | `Agent({ subagent_type: "general-purpose", model: "opus", prompt: ... })` | 별도 `codex` 프로세스를 background로 실행 (`codex exec -p '<prompt>'`) 또는 task fork |
| 파일 읽기/쓰기 | `Read` / `Edit` / `Write` | 기본 파일 도구 |
| 셸 실행 | `Bash` | 기본 shell |
| 작업 트래킹 | `TaskCreate` / `TaskUpdate` | `TODO.md` 파일 갱신 |
| 워크트리 팀 | `TeamCreate` | 별도 Codex 인스턴스를 worktree에서 가동 |
| 백그라운드 polling | `ScheduleWakeup`, `Monitor` | shell의 `tail -f`, `wait`, cron 등 |

본문 이후의 모든 "서브에이전트 호출"은 위 표의 호스트별 도구로 치환되어야 한다.

---

## 실행 흐름

### Step 0 — 사전 점검

다음을 확인하고, 부족한 정보는 사용자에게 짧게 한 번에 물어본다.

1. **프로젝트 루트 확인** — 현재 작업 디렉토리가 리뷰 대상 프로젝트의 루트인지 확인 (`git rev-parse --show-toplevel`, `ls`로 `README.md`, `package.json` 또는 `pyproject.toml` 등 존재 여부 점검). 아니면 사용자에게 경로를 묻는다.
2. **결과 저장 경로** — 통합 보고서는 `./oss-review-report.md`에 작성한다. 같은 이름이 이미 있으면 `oss-review-report-YYYYMMDD-HHMM.md`로 타임스탬프를 붙인다.
3. **교차 리뷰 사용 가능 여부** — 매번 사용자에게 다음을 물어본다 (자동 감지 금지):

   ```
   [질문] 전체 코드리뷰에서 Claude와 Codex 교차 배치를 사용할까요?
   - "예": Reviewer A = Codex(GPT-5.5), Reviewer B = Claude(Opus 4.7) — 모델 다양성으로 사각지대 보완
   - "아니오": 두 명 모두 현재 호스트(Claude 또는 Codex)의 최상위 모델로 진행
   ```

   "예"를 선택했고 현재 호스트가 Claude면 `codex:codex-rescue` 서브에이전트 또는 `codex:rescue` 슬래시 커맨드로 Codex를 외부 호출. 현재 호스트가 Codex면 별도 Claude CLI(`claude -p`)를 background로 호출. **교차 호스트는 세션 단절 가능성이 있으므로 주기적 헬스체크 필수**(아래 Step 2 참조).
4. **UI/UX 점검 대상 확인** — 프로젝트가 웹 UI를 가진 경우에만 Step 5(UI/UX)를 실행한다. CLI/라이브러리/백엔드 전용이면 사용자에게 한 줄 확인 후 Step 5를 스킵한다. 확인 질문 예: "이 프로젝트에 웹 UI가 있나요? 있다면 dev 서버 실행 명령(`npm run dev` 등)과 접속 URL을 알려주세요."

### Step 1 — 작업 트래킹 시작

다음 5개 카테고리를 작업 목록으로 만든다. UI/UX는 위 Step 0에서 스킵 결정 시 제외. Claude 호스트는 `TaskCreate`, Codex 호스트는 `TODO.md` 사용.

| # | 카테고리 | 에이전트 수 | 모델 |
|---|---------|------------|------|
| 1 | 라이센스 분석 | 1 | 현재 호스트 최상위 (Claude Opus 4.7 또는 Codex GPT-5.5) |
| 2 | 전체 코드 리뷰 | 2 | A/B 교차 (사용자 선택에 따라) |
| 3 | 보안 리뷰 | 1 | 현재 호스트 최상위 |
| 4 | 데드코드 / 레거시 / 사일런트 fallback | 1 | 현재 호스트 최상위 |
| 5 | UI/UX 점검 (Playwright) | 1 | 현재 호스트 최상위 (해당 시) |

### Step 2 — 5개 카테고리 병렬 실행

**중요**: 가능한 모든 에이전트를 **한 번에 동시에** spawn한다. 외부 호스트 호출(Codex/Claude 교차)은 background 처리.

각 에이전트 호출 시 공통 규칙:
- **모델**: 현재 호스트 최상위 모델 (Claude Opus 4.7 또는 Codex GPT-5.5) — 절대 생략하지 마라.
- **prompt 첫 줄**: 호스트별 식별 문구 삽입 (위 핵심원칙 2번 참조).
- **prompt 본문**: 카테고리별 references 파일 내용을 그대로 임베드한다. references 디렉토리의 해당 .md 파일을 먼저 읽은 뒤 본문을 prompt에 직접 넣는다. 서브에이전트는 references 파일 경로만 받아도 접근 가능하지만, 새 컨텍스트에서 길을 잃지 않도록 본문을 직접 넣는 편이 안전하다.
- **결과 저장 경로**: prompt 마지막에 `<프로젝트루트>/.oss-review/<카테고리>.md`로 명시. 사전에 `mkdir -p .oss-review`로 폴더를 만들어 둔다.

#### 카테고리별 호출 사양

**1. 라이센스 분석 (references/01-license.md)**
- 현재 호스트 최상위 모델로 1명 호출
- 결과 저장: `.oss-review/01-license.md`
- 출력: 의존성/참고 프로젝트 라이센스 호환성, README/LICENSE/NOTICE 반영 여부

**2-A. 전체 코드 리뷰 - Reviewer A (references/02-codereview.md)**
- 교차 배치 "예" 선택 시: 현재 호스트가 Claude면 → Codex 호출, 현재 호스트가 Codex면 → Claude 호출
- 교차 배치 "아니오" 선택 시: 현재 호스트 최상위 모델 그대로
- prompt에 "당신은 Reviewer A입니다. Reviewer B와 독립적으로 리뷰하세요"를 명시
- 결과 저장: `.oss-review/02-codereview-A.md`

**2-B. 전체 코드 리뷰 - Reviewer B (references/02-codereview.md)**
- 항상 현재 호스트 최상위 모델
- prompt는 2-A와 **완전히 동일**. 단, "당신은 Reviewer B입니다"로 식별만 다르게.
- 결과 저장: `.oss-review/02-codereview-B.md`

**3. 보안 리뷰 (references/03-security.md)**
- 현재 호스트 최상위 모델로 1명 호출
- 결과 저장: `.oss-review/03-security.md`

**4. 데드코드 / 레거시 / 사일런트 fallback (references/04-deadcode.md)**
- 현재 호스트 최상위 모델로 1명 호출
- 결과 저장: `.oss-review/04-deadcode.md`

**5. UI/UX 점검 (references/05-ux.md)**
- 현재 호스트 최상위 모델로 1명 호출
- prompt에 **dev 서버가 이미 떠 있다는 가정**(사용자가 미리 띄움)과 접속 URL을 명시
- `playwright-cli` 바이너리(`~/.nvm/versions/node/v20.20.1/bin/playwright-cli`)를 셸로 호출하여 다크/라이트/모바일 viewport 스크린샷을 캡처하고 시각적 이슈를 보고하도록 지시
- 스크린샷 저장: `.oss-review/screenshots/`
- 결과 저장: `.oss-review/05-ux.md`

#### 교차 호스트 헬스체크 (교차 배치 사용 시에만)

외부 호스트(Claude→Codex 또는 Codex→Claude) 호출은 세션 단절 가능성이 있다. background로 띄우고, 다른 4개 에이전트가 종료되기 전까지 다음을 주기적으로 수행한다:

1. **5분(`ScheduleWakeup` 사용 시 ~270초)마다 상태 확인**
   - Claude 호스트 → Codex 호출 시: `TaskGet`/`TaskOutput`으로 Codex 작업 출력 확인
   - Codex 호스트 → Claude 호출 시: background로 띄운 `claude -p` 프로세스의 stdout 확인 (`tail -f`)
2. **응답 끊김/에러 감지 시**: 즉시 사용자에게 보고 후, **같은 prompt로 현재 호스트 최상위 모델 백업 에이전트 1명을 spawn하여 자리를 대체한다**. 통합 보고서에 "Reviewer A는 [Codex/Claude] 실패로 [Claude/Codex] 백업으로 교체됨"을 명시한다.
3. **헬스체크 도중 다른 에이전트가 완료되어도 종료하지 말고**, 외부 호스트 결과까지 기다린 후 통합 단계로 진입.

### Step 3 — 결과 수집 & 통합 보고서 작성

모든 에이전트가 완료되면:

1. `.oss-review/` 아래 모든 .md를 읽는다.
2. **두 명의 코드 리뷰어(2-A, 2-B) 결과는 합집합으로 다루되, 동일 이슈는 1건으로 합치고 두 명 모두 지적한 항목은 신뢰도 ★★★로 표시한다.** 한 명만 지적한 항목은 ★★ (검증 필요), 명백히 잘못된 지적은 별도 섹션으로 빼지 말고 통합 보고서에서 누락시킨다.
3. `./oss-review-report.md` (또는 타임스탬프 버전)을 다음 구조로 작성한다.

```markdown
# OSS Review Report — {프로젝트명} ({YYYY-MM-DD HH:MM})

## 0. Executive Summary
- 총 발견 이슈 수: P0 X건 / P1 Y건 / P2 Z건
- 호스트: {Claude Opus 4.7 | Codex GPT-5.5}, 교차 배치: {예/아니오}
- 가장 위험한 3가지
- 출시 가능 여부 판단 (Go / No-Go / Conditional)

## 1. 라이센스 분석
(요약 + 문제 항목 표)

## 2. 코드 리뷰 통합 (Reviewer A: {Claude|Codex} / Reviewer B: {Claude|Codex})
| 우선순위 | 이슈 | 위치 | 합의 | 권장 조치 |
|----------|-----|------|------|----------|
| P0 | ... | path/to/file:LL | ★★★ | ... |

## 3. 보안 리뷰
(취약점 표 + 권장 패치)

## 4. 데드코드/레거시/사일런트 fallback
(파일별 정리)

## 5. UI/UX 점검
(스크린샷 링크 포함, 다크/라이트/모바일 별)

## 6. 수정 제안 — 사용자 승인 대기
### 6.1 즉시 직접 수정 가능 (간단 작업)
- [ ] {파일경로:라인} — {1줄 설명}
- ...

### 6.2 워크트리 + 팀 작업 필요 (복잡 작업)
- [ ] {제목} — {영향 범위 / 변경 파일 수 / 권장 브랜치명}
- ...

## 7. 다음 단계
사용자가 6.1 / 6.2 중 어떤 항목을 진행할지 선택해주세요.
```

4. 작성 후 사용자에게 **요약 메시지**(보고서 핵심 5~10줄)와 함께 보고서 경로를 제시한다. 절대 자동으로 수정에 들어가지 않는다.

### Step 4 — 사용자 승인 후 수정 진행

사용자가 어떤 항목을 진행할지 선택하면 분류 후 처리:

**간단 작업 (single-file, 명백한 1줄 수정, 오타, 누락된 라이센스 표기 추가 등)**
- 메인 컨텍스트에서 직접 수정 (Claude → `Edit`/`Write`, Codex → 기본 파일 도구)
- 수정 후 변경 요약을 한 줄로 보고하고 다음 항목으로 이동

**복잡 작업 (다중 파일, 리팩터, 보안 패치 + 테스트, UI 구조 변경 등)**
- 새 워크트리를 생성한다:
  ```bash
  git worktree add ../worktree-oss-review-fix -b fix/oss-review-{topic}
  ```
- 해당 worktree 디렉토리로 이동한 후 팀을 소집한다. 팀 구성 예시:
  - 1명: 실제 코드 변경 (현재 호스트 최상위 모델, code-architect 또는 general-purpose)
  - 1명: 테스트 작성/실행
  - 1명: 변경 리뷰 (code-reviewer 류)
- Claude 호스트: `TeamCreate` 사용 / Codex 호스트: 별도 Codex 인스턴스를 worktree에서 실행
- 팀 작업이 끝나면 main 컨텍스트로 돌아와 변경 사항을 사용자에게 보고하고, `gh pr create` 또는 머지 여부는 다시 사용자에게 묻는다.

수정이 끝나면:
- `.oss-review/` 와 임시 보고서는 사용자가 명시적으로 "정리해줘"라고 할 때까지 그대로 둔다.
- 작업 완료 후 추가 리뷰가 필요하면 본 스킬을 다시 실행하면 된다.

---

## references 파일 사용 규칙

이 스킬의 본체는 짧게 유지하고, 카테고리별 상세 점검 지시는 `references/0X-*.md`에 분리해 두었다. Step 2에서 각 서브에이전트를 spawn하기 전에 해당 references 파일을 읽은 다음, 그 내용을 prompt에 그대로 임베드한다. 서브에이전트는 처음부터 끝까지 한 메시지로 지시를 받아야 길을 잃지 않는다.

| 파일 | 용도 |
|------|------|
| `references/01-license.md` | 라이센스 분석 서브에이전트 프롬프트 |
| `references/02-codereview.md` | 전체 코드 리뷰 (A/B 공통) 프롬프트 |
| `references/03-security.md` | 보안 리뷰 서브에이전트 프롬프트 |
| `references/04-deadcode.md` | 데드코드/레거시/사일런트 fallback 프롬프트 |
| `references/05-ux.md` | UI/UX (Playwright) 점검 프롬프트 |

각 references 파일은 호스트 중립적으로 작성되어 있다 — "당신은 시니어 리뷰어다"로 시작하고 모델명을 가정하지 않는다. 메인 컨텍스트가 호출 시점에 첫 줄에 호스트별 식별 문구를 덧붙인다.

---

## 자주 빠지기 쉬운 함정

- **컨텍스트 재사용 금지**: 직전 세션의 에이전트 결과를 `SendMessage`(Claude) 또는 task resume(Codex)으로 이어가지 말 것. 본 스킬의 본질은 "오염되지 않은 새 시선"이다.
- **모델 다운그레이드 금지**: 비용 절약 목적으로 Sonnet/Haiku 또는 GPT-5/5.1 사용 금지. 사용자가 명시적으로 요구하지 않는 한 항상 최상위 모델.
- **교차 호스트 결과를 맹신하지 말 것**: 외부 호스트가 끊기지 않고 결과를 줬더라도, 같은 호스트 Reviewer B와의 교차 검증으로 신뢰도 ★를 매겨라.
- **자동 수정 금지**: "사소해 보여서" 라는 이유로 사용자 승인 없이 패치를 적용하면 안 된다. Executive Summary와 6.1/6.2 분류 후 반드시 승인을 기다린다.
- **UI 점검에서 dev 서버 자동 실행 금지**: 사용자에게 미리 띄워달라고 부탁하고 URL만 받는다. 백그라운드 프로세스가 환경을 오염시킬 수 있다.
- **playwright MCP가 아니라 `playwright-cli` 바이너리**: 사용자 글로벌 지침(CLAUDE.md / AGENTS.md)에 따라 항상 CLI 바이너리를 셸로 호출한다.
