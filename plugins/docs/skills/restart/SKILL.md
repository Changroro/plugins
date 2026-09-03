---
name: restart
description: Rebuilds project memory by type from existing documents, current code and configuration, and the conversation. Recreates AGENTS from agent/developer work behavior only and routes product semantics elsewhere instead of appending accumulated files. Use for "restart", "AGENTS 완전 재설정", "AGENTS 다시 작성", "메모리 초기화", "메모리 재구성", "rebuild agents", and "rebuild project memory".
---

# Restart Project Memory

Rebuild agent memory from current evidence. This replaces accumulated memory; it does not append to it or reset source code.

## Workflow

1. Read the conversation; every root and nested AGENTS, AGENTS.override, CLAUDE, and HANDOFF file; canonical project documents; and enough current code, config, tests, and hooks to verify candidates.
2. Resolve conflicts in this order: current user decisions, current config and tests, current repository state, then git history. Existing memory is evidence to verify, not authority merely because it exists.
3. Read `../handover/references/routing.md` and classify every item by memory type before considering evidence. Product behavior, domain rules, field/API semantics, architecture, UI behavior, and notification policy can never enter AGENTS.
4. Read `../handover/references/semantic-review.md` and run its mandatory independent critic loop on the complete AGENTS draft. Any rejection or uncertainty is routed to a scoped document. If no independent subagent is available, ask before changing AGENTS.
5. Recreate each AGENTS file from accepted `agent_policy` rules only. Move rules to the narrowest valid scope and remove obsolete scopes or overrides that have no distinct role.
6. Preserve Claude-only instructions while repairing effective AGENTS imports. Keep tracked repository-owned files tracked; require separate evidence before treating a repository as external.
7. Rewrite planning, development, operations, global, and task-state memory according to its type, then rewrite HANDOFF from the current continuation only.
8. Run the shared auditor with the critic's temporary review artifact and fix every violation:

```bash
python3 <restart-skill-directory>/../handover/scripts/audit.py --root . --mode full --review-file <temporary-review-json>
```

The auditor checks mechanical boundaries and review integrity; the independent critic owns semantic judgment.

## User communication

After success, respond with `완료.` followed only by memory-document paths under `추가:` and `수정:`. Omit empty sections; when no file changed, respond only `완료.` Do not include content summaries, audit results, classifications, moved or deleted text, stale items, or versions. Ask one concise question only when authorization or unresolved ambiguity blocks correct execution.

## References

- `../handover/references/routing.md` — promotion gate and destinations
- `../handover/references/semantic-review.md` — mandatory independent review and audit artifact
- `../handover/references/templates.md` — rebuilt file shapes
- `../handover/references/edge-cases.md` — ownership, overrides, gitignore, and ambiguous targets
