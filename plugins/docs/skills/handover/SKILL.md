---
name: handover
description: Prepares a focused project handoff from the current conversation. Updates HANDOFF.md, routes product and implementation knowledge to scoped documents, and updates AGENTS.md only for evidenced agent/developer work behavior, never product semantics. Use for "인수인계", "세션 인계", "handover", "handoff 업데이트", "agents.md 최신화", "update agents md", "write handoff", and the pre-PR pattern "README / AGENTS.md / HANDOFF".
---

# Handover

Prepare the next session from the conversation without requiring `remember`. Update only session-relevant memory; use `$restart` for a project-wide rebuild.

## Workflow

1. Read the current conversation, effective AGENTS and CLAUDE files from repository root to the working directory, HANDOFF.md, and only documents relevant to this session.
2. Extract candidate memories without assigning destinations or treating repetition as a type decision.
3. Read `references/routing.md`. Apply its type gate before evidence: product behavior, domain rules, field/API semantics, architecture, UI behavior, and notification policy can never enter AGENTS. Update AGENTS only for `agent_policy` candidates that pass every admission condition.
4. Run the independent critic loop on proposed AGENTS additions. Any rejection or uncertainty is routed to a scoped document, not promoted or sent to the user for classification.
5. Route durable non-rule knowledge into the project's existing planning, development, or operations documents at the narrowest relevant scope. Create one focused topic document only when no suitable system exists.
6. Verify facts against current user decisions, config and tests, current state, then git history. Earlier history never overrides the current user.
7. Merge by meaning instead of appending a conversation dump. Do not reclassify unrelated old content.
8. Rewrite HANDOFF.md as one just-completed outcome plus concrete next work and real blockers. Exclude history, metrics, SHAs, dates, and live process state.
9. Preserve Claude-only instructions while ensuring the effective AGENTS file is imported. Treat tracked files as repository-owned; require separate evidence before using an external-repository override.
10. Run the auditor and fix every violation. Repeat `--agents-file` for each AGENTS file modified; omit it when none changed:

```bash
python3 <handover-skill-directory>/scripts/audit.py --root . --mode routine --agents-file <modified-AGENTS-path>
```

The auditor checks mechanical boundaries; promotion remains a judgment step.

## User communication

Do not report audit results, changed files, promoted, moved, deleted, or stale items, versions, or summaries. If no user decision is needed, respond only `완료.` Ask one concise question only when authorization or unresolved ambiguity blocks correct execution.

## References

- `references/routing.md` — promotion evidence and destinations
- `references/templates.md` — memory file shapes
- `references/edge-cases.md` — ownership, overrides, gitignore, and ambiguous targets
