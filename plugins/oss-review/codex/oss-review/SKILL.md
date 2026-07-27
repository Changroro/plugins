---
name: oss-review
description: "사용자가 자신이 개발한 프로젝트·레포·오픈소스를 출시·공개·릴리즈·배포 전에 전체적으로 점검·검수·리뷰받고 싶어 할 때 사용하는 종합 리뷰 스킬. 라이센스(참고한 레포 라이센스의 README/LICENSE 반영 포함), 전체 코드리뷰(Codex GPT-5.5와 Claude Opus 4.7 교차 2인 병렬), 보안 취약점, 데드코드·레거시·사일런트 fallback, UI/UX(다크·라이트·모바일 화면을 agent-browser로 점검)의 5개 영역을 각각 새 세션(codex exec)으로 병렬 점검하고 하나의 통합 보고서를 만든 뒤 승인을 받아 수정한다. 다음과 같은 경우 'oss-review'라고 명시하지 않더라도 반드시 이 스킬을 사용한다 — '내 프로젝트/레포/오픈소스 리뷰해줘·점검해줘·검수해줘', '공개 전 점검', '출시 전 검수', '릴리즈 전 검토', '깃헙에 올리기 전 점검', '배포 전 검수', 'v1.0/태그 달기 전 코드리뷰', 'codex랑 claude 둘 다 써서 코드리뷰', 그리고 코드·보안·라이센스·UI·데드코드 중 둘 이상을 함께 봐달라거나 출시·공개 준비가 됐는지 다각도로 판단해 달라는 요청. 단일 PR 한 건 리뷰나 한 가지 측면만 점검하는 요청에는 전용 도구를 쓴다."
---

# oss-review (Codex 판): 오픈소스 프로젝트 종합 리뷰

> 이 스킬은 **Codex CLI 전용 변환본**이다. Claude Code 판은 동일 이름으로 별도 존재하며, 본 판은 Codex의 도구(`codex exec`, shell, `TODO.md`)에 맞게 변환되어 있다.

사용자가 개발한 오픈소스 프로젝트를 출시/공개 전 마지막으로 점검하기 위한 멀티-에이전트 리뷰 파이프라인이다. 매 호출마다 **새 세션(독립 컨텍스트)**의 서브에이전트를 5개 카테고리에 걸쳐 병렬 실행하고, 결과를 **하나의 통합 보고서**로 사용자에게 제시한 뒤, **사용자 승인 후에만 수정 작업**으로 진입한다.

## 핵심 원칙 (반드시 준수)

1. **매번 새 세션(새 컨텍스트)**: 각 카테고리 리뷰는 `codex exec`로 **새 프로세스를 띄워** 실행한다. `codex exec`는 매번 깨끗한 새 세션을 시작하므로 이전 대화 맥락이 결과를 오염시키지 않는다. **`codex exec resume`을 쓰지 마라** — 새 시선이 본 스킬의 핵심이다.
2. **모델: 최상위 모델 고정**:
   - **Codex 자리**: 반드시 **`gpt-5.5`**. `codex exec -m gpt-5.5 ...` (가능하면 `-c model_reasoning_effort=xhigh`).
   - **교차 배치로 부르는 Claude 자리**: 반드시 **Claude Opus 4.7** (`claude -p --model claude-opus-4-7`).
   - 그 미만 모델(gpt-5/5.1, Sonnet/Haiku)로 다운그레이드 금지. 비용보다 결과 품질이 중요한 단계다.
   - 추가 안전장치: 각 서브에이전트 prompt 첫 줄에 식별 문구를 박는다 — `"당신은 Codex/GPT-5.5 모델로 호출된 리뷰어입니다."` (Claude 교차 자리는 `"당신은 Claude Opus 4.7 모델로 호출된 리뷰어입니다."`)
3. **읽기 전용 분석**: 5개 서브에이전트는 분석/보고만 하고 **코드를 직접 수정하지 않는다**. 서브에이전트는 `--sandbox read-only`로 띄워 이를 강제한다. 수정은 본 스킬(메인 세션)이 통합 보고서로 사용자에게 보고 → 승인 → 적용 순서로만 진행한다.
4. **승인 게이트**: 어떤 수정도 사용자가 명시적으로 "진행" "OK" "승인" 등의 의사를 표시하기 전에는 시작하지 않는다.
5. **간단한 작업은 직접 / 복잡한 작업은 워크트리 + 분리 세션**: 승인 후 수정 단계에서 단일 파일 수준의 트리비얼 수정은 메인 세션에서 직접 처리하고, 다중 파일·구조 변경·아키텍처 수정 등은 `git worktree`를 새로 파고 별도 `codex exec` 세션을 그 워크트리에서 가동해 격리된 브랜치에서 진행한다.

---

## Codex 실행 메커니즘

| 추상 작업 | Codex 구현 |
|----------|-----------|
| 새 컨텍스트 서브에이전트 | `codex exec -m gpt-5.5 --sandbox read-only '<prompt>'` 를 background(`&`)로 실행 |
| 교차 배치(Claude) 호출 | `claude -p --model claude-opus-4-7 '<prompt>'` 를 background로 실행 |
| 코드리뷰 특화(선택) | `codex exec review` 서브커맨드 활용 가능 |
| 작업 트래킹 | 프로젝트 루트의 `TODO.md` 갱신 (`.gitignore`에 추가) |
| 병렬 실행 | 여러 `codex exec ... &`를 동시에 띄우고 PID 수집 후 `wait` |
| 진행 모니터링 | 각 프로세스 stdout을 파일로 리다이렉트하고 `tail -f`로 확인 |
| 워크트리 팀 | worktree 안에서 별도 `codex exec` 세션 가동 |

**서브에이전트 출력 캡처 패턴**:
```bash
mkdir -p .oss-review
codex exec -m gpt-5.5 --sandbox read-only "$(cat prompt-01-license.txt)" \
  > .oss-review/01-license.md 2>.oss-review/01-license.err &
PID_LICENSE=$!
# ... 나머지 카테고리도 동일하게 & 로 병렬 기동 ...
wait $PID_LICENSE $PID_SECURITY $PID_DEADCODE $PID_UX ...
```
각 서브에이전트에게 "결과를 표준출력으로만 내라"고 지시하거나, prompt 안에서 직접 `.oss-review/<카테고리>.md`에 쓰도록 지시한다(이 경우 `--sandbox workspace-write`가 필요하므로, 읽기전용 강제와 상충하지 않게 출력 캡처 방식을 권장).

---

## 실행 흐름

### Step 0 — 사전 점검

1. **프로젝트 루트 확인** — `git rev-parse --show-toplevel`, `ls`로 `README.md`, `package.json`/`pyproject.toml` 등 확인. 아니면 사용자에게 경로를 묻는다.
2. **결과 저장 경로** — 통합 보고서는 `./oss-review-report.md`. 이미 있으면 `oss-review-report-YYYYMMDD-HHMM.md`.
3. **교차 리뷰 사용 여부** — 매번 사용자에게 묻는다:
   ```
   [질문] 전체 코드리뷰에서 Codex와 Claude 교차 배치를 사용할까요?
   - "예": Reviewer A = Codex(gpt-5.5), Reviewer B = Claude(claude-opus-4-7) — 모델 다양성으로 사각지대 보완
   - "아니오": 두 명 모두 Codex(gpt-5.5)
   ```
   "예"이고 `claude` CLI가 설치돼 있으면(`command -v claude`) Claude를 교차 호출. 없으면 사용자에게 알리고 두 명 모두 Codex로 진행. **교차 호스트는 세션 단절 가능성이 있으므로 주기적 헬스체크 필수**(Step 2 참조).
4. **UI/UX 점검 대상 확인** — 웹 UI가 있는 경우에만 Step 5 실행. CLI/라이브러리/백엔드 전용이면 스킵. "웹 UI가 있나요? 있으면 dev 서버 명령과 접속 URL을 알려주세요."

### Step 1 — 작업 트래킹 시작

프로젝트 루트에 `TODO.md`를 만들어 5개 카테고리를 기록(`.gitignore`에 `TODO.md` 추가). UI/UX는 스킵 시 제외.

| # | 카테고리 | 에이전트 수 | 모델 |
|---|---------|------------|------|
| 1 | 라이센스 분석 | 1 | Codex gpt-5.5 |
| 2 | 전체 코드 리뷰 | 2 | A/B 교차(사용자 선택) |
| 3 | 보안 리뷰 | 1 | Codex gpt-5.5 |
| 4 | 데드코드 / 레거시 / 사일런트 fallback | 1 | Codex gpt-5.5 |
| 5 | UI/UX 점검 (agent-browser) | 1 | Codex gpt-5.5 (해당 시) |

### Step 2 — 5개 카테고리 병렬 실행

**중요**: 모든 서브에이전트를 `codex exec ... &`로 **동시에** 기동하고 PID를 모은다. 교차 배치의 Claude 자리는 `claude -p ... &`로 띄운다.

각 서브에이전트 prompt 구성:
- **첫 줄**: 식별 문구(핵심원칙 2번).
- **본문**: 카테고리별 references 파일 내용을 그대로 임베드한다. 해당 `references/0X-*.md`를 읽어 prompt에 직접 넣는다.
- **끝**: 출력은 표준출력으로만 내라고 지시(메인 세션이 `.oss-review/<카테고리>.md`로 리다이렉트). 단, 서브에이전트가 직접 파일을 써야 하면 그 자리만 `--sandbox workspace-write`로 띄운다.

#### 카테고리별 사양

**1. 라이센스 분석 (references/01-license.md)** → `.oss-review/01-license.md`
**2-A. 코드 리뷰 Reviewer A (references/02-codereview.md)**
- 교차 "예": `claude -p --model claude-opus-4-7` (Claude). 교차 "아니오": `codex exec -m gpt-5.5`.
- prompt에 "당신은 Reviewer A입니다. Reviewer B와 독립적으로 리뷰하세요" 명시 → `.oss-review/02-codereview-A.md`
**2-B. 코드 리뷰 Reviewer B (references/02-codereview.md)**
- 항상 `codex exec -m gpt-5.5`. prompt는 2-A와 동일, "당신은 Reviewer B입니다"만 다르게 → `.oss-review/02-codereview-B.md`
- 참고: Codex 자리는 `codex exec review`로 레포 전체 리뷰를 병행해도 좋다.
**3. 보안 리뷰 (references/03-security.md)** → `.oss-review/03-security.md`
**4. 데드코드/레거시/사일런트 fallback (references/04-deadcode.md)** → `.oss-review/04-deadcode.md`
**5. UI/UX (references/05-ux.md)** → `.oss-review/05-ux.md`
- dev 서버가 이미 떠 있다고 가정, 접속 URL을 prompt에 명시.
- `agent-browser` CLI를 shell로 호출해 다크/라이트/모바일 스크린샷 캡처. 스크린샷은 `.oss-review/screenshots/`.
- 이 자리는 화면 캡처가 필요하므로 `--sandbox workspace-write`로 띄운다.

#### 교차 호스트 헬스체크 (교차 배치 사용 시에만)

`claude -p` 외부 호출은 세션 단절 가능성이 있다. background로 띄우고 다른 에이전트가 끝나기 전까지:
1. **주기적으로(약 5분) 상태 확인**: `tail -n 20 .oss-review/02-codereview-A.md` 와 프로세스 생존(`kill -0 $PID_A 2>/dev/null`) 점검.
2. **끊김/에러 감지 시**: 즉시 사용자에게 보고 후, 같은 prompt로 `codex exec -m gpt-5.5` 백업을 띄워 자리를 대체. 통합 보고서에 "Reviewer A는 Claude 실패로 Codex 백업으로 교체됨" 명시.
3. **다른 에이전트가 먼저 끝나도 종료하지 말고** 외부 호스트 결과까지 `wait` 후 통합 단계로 진입.

### Step 3 — 결과 수집 & 통합 보고서 작성

1. `.oss-review/` 아래 모든 `.md`를 읽는다(`.err`도 확인해 에이전트 실패 여부 점검).
2. 두 코드 리뷰어 결과는 합집합으로 다루되, 동일 이슈는 1건으로 합치고 둘 다 지적한 항목은 신뢰도 ★★★, 한 명만 지적한 항목은 ★★(검증 필요). 명백한 오탐은 통합 보고서에서 제외.
3. `./oss-review-report.md`를 다음 구조로 작성:

```markdown
# OSS Review Report — {프로젝트명} ({YYYY-MM-DD HH:MM})

## 0. Executive Summary
- 총 발견 이슈 수: P0 X건 / P1 Y건 / P2 Z건
- 호스트: Codex gpt-5.5, 교차 배치: {예/아니오}
- 가장 위험한 3가지
- 출시 가능 여부 판단 (Go / No-Go / Conditional)

## 1. 라이센스 분석
## 2. 코드 리뷰 통합 (Reviewer A: {Codex|Claude} / Reviewer B: Codex)
## 3. 보안 리뷰
## 4. 데드코드/레거시/사일런트 fallback
## 5. UI/UX 점검 (스크린샷 링크 포함)

## 6. 수정 제안 — 사용자 승인 대기
### 6.1 즉시 직접 수정 가능 (간단 작업)
### 6.2 워크트리 + 분리 세션 필요 (복잡 작업)

## 7. 다음 단계
```

4. 작성 후 사용자에게 요약 메시지(핵심 5~10줄) + 보고서 경로 제시. 자동으로 수정에 들어가지 않는다.

### Step 4 — 사용자 승인 후 수정 진행

**간단 작업**: 메인 세션에서 직접 파일 수정. 변경 요약을 한 줄로 보고.

**복잡 작업**:
```bash
git worktree add ../worktree-oss-review-fix -b fix/oss-review-{topic}
```
worktree 안에서 별도 `codex exec` 세션을 가동해 변경/테스트/자체리뷰를 수행. 끝나면 메인 세션으로 돌아와 보고하고 `gh pr create`/머지 여부를 사용자에게 묻는다.

수정 후 `.oss-review/`와 임시 보고서는 사용자가 "정리해줘"라고 할 때까지 남겨둔다.

---

## references 파일 사용 규칙

카테고리별 상세 점검 지시는 `references/0X-*.md`에 있다. 각 서브에이전트를 `codex exec`로 띄우기 전에 해당 파일을 읽어 prompt에 그대로 임베드한다(파일은 호스트 중립으로 작성됨). 메인 세션이 호출 시점에 첫 줄 식별 문구만 덧붙인다.

| 파일 | 용도 |
|------|------|
| `references/01-license.md` | 라이센스 분석 |
| `references/02-codereview.md` | 전체 코드 리뷰 (A/B 공통) |
| `references/03-security.md` | 보안 리뷰 |
| `references/04-deadcode.md` | 데드코드/레거시/사일런트 fallback |
| `references/05-ux.md` | UI/UX (agent-browser) |

---

## 자주 빠지기 쉬운 함정

- **세션 재사용 금지**: `codex exec resume`으로 직전 세션을 잇지 마라. 매번 새 `codex exec`로 깨끗한 컨텍스트를 띄운다.
- **모델 다운그레이드 금지**: gpt-5/5.1이나 Claude Sonnet/Haiku로 내리지 마라. 항상 gpt-5.5 / claude-opus-4-7.
- **읽기전용 강제**: 분석 서브에이전트는 `--sandbox read-only`로 띄워 코드 수정을 원천 차단. UI 캡처 자리만 예외.
- **교차 결과 맹신 금지**: Claude 교차 결과도 Codex Reviewer B와 교차 검증해 신뢰도 ★를 매겨라.
- **자동 수정 금지**: 사용자 승인 없이 패치 금지. Executive Summary + 6.1/6.2 분류 후 승인 대기.
- **dev 서버 자동 실행 금지**: 사용자에게 미리 띄워달라고 부탁하고 URL만 받는다.
- **브라우저 점검은 `agent-browser` CLI**: 사용자 글로벌 지침(AGENTS.md)에 따라 agent-browser를 shell로 호출.
