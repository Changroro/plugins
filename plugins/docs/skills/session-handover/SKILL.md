---
name: session-handover
description: Maintains cross-tool project memory so a fresh session in any agent (Claude Code, Codex, Cursor, Gemini CLI) resumes without re-explanation — durable rules in AGENTS.md, a one-line `@AGENTS.md` shim in CLAUDE.md, a rolling next-step log in HANDOFF.md, topical knowledge in docs/ files it creates as needed. Audits and re-routes existing content on every run, then verifies the result mechanically. Use whenever the user asks to write, update, clean up, or sync project memory, session docs, or the next-step log — including "agents.md 최신화", "agents.md 정리", "handoff 업데이트", "인수인계", "세션 인계", "기획 문서로 옮겨", "update agents md", "write handoff", "session handover", "sync memory bank", and the pre-PR pattern "README / AGENTS.md / HANDOFF".
---

# Session Handover

Maintains project files so a fresh AI session — in any tool — can resume work without re-explanation. Each file has one job:

| File | Job | Loaded |
| --- | --- | --- |
| **AGENTS.md** | Durable rules another tool also needs: user-given rules, conventions, cautions, non-obvious env facts. | Every session, every tool → the expensive one. |
| **CLAUDE.md** | One line: `@AGENTS.md`. Never holds content of its own. | Every Claude session. |
| **HANDOFF.md** | Rolling "just done / next up". | Read at session start. |
| **docs/\<topic\>.md** | Durable knowledge that is not a rule — planning, specs, design decisions, troubleshooting lore. One topic per file. | On demand only. |

Everything here is written for the next AI session, not for a human. If a human is the only reader who benefits from a line, cut it.

## The judgment this skill exists to apply

AGENTS.md is the only file loaded unconditionally, so its lines are the only ones that cost context forever — and a bloated memory file is one agents start ignoring. **When in doubt, route away from AGENTS.md.**

Two filters decide whether a line survives, wherever it came from — this session, or a hand-edit made months ago:

1. **Rediscoverable?** Learnable from the code, `ls`, or `git log` → out.
2. **Load-bearing?** Would removing it make the next session get something wrong? No → cut.

The second filter also settles duplication: a rule already in the user's global memory or auto-memory does not get restated here.

## Workflow

**1. Gather.** Read existing AGENTS.md / CLAUDE.md / HANDOFF.md and any `docs/` session files, but treat them as possibly stale — verify against `git status` and `git log --oneline -10`. When `git log` and the prose disagree, the prose is wrong.

**2. Route.** Sort this session's content and every pre-existing line by kind: rules → AGENTS.md, topical knowledge → a fitting `docs/` doc, finished step + next actions → HANDOFF.md. Misplaced content gets **moved**, never silently dropped. Read `references/routing.md` when a destination is unclear or you are auditing an unfamiliar file.

**3. Merge by meaning, not text.** Preserve still-true meaning; add, refine, or remove only in response to something explicit in this session. Text is not sacred — relocating and compressing is the job. "Still true" is a verdict: check each preserved fact against the code and this session. An unconfirmable literal (limit, size, URL, workflow) is a stale candidate — update it if this session shows the current value, otherwise keep it and list it as unverified in the report.

HANDOFF.md is regenerable — replace it wholesale with the new snapshot.

**4. Write.** Directly. Do not ask "작성할까요?" / "shall I write this?". Gitignore what you wrote (`references/edge-cases.md`).

**5. Verify.** Run the audit, fix what it reports, re-run until it exits 0:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/session-handover/scripts/audit.py" --root .
```

It settles what a machine can settle — budgets, the CLAUDE.md shim, volatile literals, HANDOFF pollution, gitignore state, upstream-tracked fallbacks. It cannot judge routing, compression, or whether a line is load-bearing. Those stay yours.

**6. Report.** The audit's summary line, then only what changed:

```
AGENTS.md 58줄 · HANDOFF.md 12줄 · audit 11/11
moved: docs/<file> ← <n>줄 (<half-line gist>)
cut: "<deleted line, verbatim>"
stale 유지: <unverified entries>
```

Pre-existing lines you deleted are quoted verbatim — the files are gitignored, so this report is the only recovery path. Moved content names its destination instead. Cuts from this session's own draft need no listing. Never mention this skill, its version, or its rules; the report is about the files. No closing narration, no "다음 세션은 …하면 됩니다".

## Non-negotiable

Everything above is judgment except these — they are contracts, and `audit.py` enforces them:

- **Budgets.** AGENTS.md ≤60 lines target, ~100 hard. HANDOFF.md ≤15.
- **CLAUDE.md is a shim**, exactly one line, forever.
- **Nothing pre-existing disappears unreported.**
- **Upstream-tracked files are never overwritten**, and tracked files are never gitignored.
- **Verify the target directory when ambiguous.** Wrong-project writes surface late — this is the one thing worth asking about.

## References

`${CLAUDE_PLUGIN_ROOT}/skills/session-handover/references/` 아래. 필요할 때만 읽는다:

- `references/routing.md` — routing table, the three memory layers, docs/ conventions
- `references/templates.md` — AGENTS / CLAUDE / HANDOFF file shapes
- `references/edge-cases.md` — upstream-tracked fallback, gitignore rules, non-git projects
