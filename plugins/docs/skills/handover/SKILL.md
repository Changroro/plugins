---
name: handover
description: Prepares a focused project handoff from the current conversation. Updates HANDOFF.md, routes durable decisions and procedures to scoped project documents, and updates AGENTS.md only for evidenced mandatory project behavior. Use for "인수인계", "세션 인계", "handover", "handoff 업데이트", "agents.md 최신화", "update agents md", "write handoff", and the pre-PR pattern "README / AGENTS.md / HANDOFF".
---

# Handover

Prepare the next session from the conversation without requiring `remember`. Update only session-relevant memory; use `$restart` for a project-wide rebuild.

## Workflow

1. Read the current conversation, effective AGENTS and CLAUDE files from repository root to the working directory, HANDOFF.md, and only documents relevant to this session.
2. Collect new or corrected conventions, repeated project-specific preferences, feature decisions, exact procedures, verified recurring failures, the completed outcome, next actions, and blockers.
3. Read `references/routing.md`. Update AGENTS only when all seven promotion conditions pass, and place the rule in the narrowest scope. A durable project preference such as port 3002 can qualify; a feature request, implementation mapping, command transcript, or general work style cannot.
4. Route durable non-rule knowledge into the project's existing planning, development, or operations documents at the narrowest relevant scope. Create one focused topic document only when no suitable system exists.
5. Verify facts against current user decisions, config and tests, current state, then git history. Earlier history never overrides the current user.
6. Merge by meaning instead of appending a conversation dump. Do not reclassify unrelated old content.
7. Rewrite HANDOFF.md as one just-completed outcome plus concrete next work and real blockers. Exclude history, metrics, SHAs, dates, and live process state.
8. Preserve Claude-only instructions while ensuring the effective AGENTS file is imported. Treat tracked files as repository-owned; require separate evidence before using an external-repository override.
9. Run the auditor and fix every violation:

```bash
python3 <handover-skill-directory>/scripts/audit.py --root . --mode routine
```

The auditor checks mechanical boundaries; promotion remains a judgment step.

## Report

Report the audit total and material changes only: promoted rules with evidence, moved knowledge with its destination, and unverified stale entries. Quote every deleted pre-existing line verbatim because local memory may not have git recovery. Do not mention this skill or its version.

## References

- `references/routing.md` — promotion evidence and destinations
- `references/templates.md` — memory file shapes
- `references/edge-cases.md` — ownership, overrides, gitignore, and ambiguous targets
