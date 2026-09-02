---
name: restart
description: Rebuilds project memory from existing documents, current code and configuration, and the conversation. Recreates the AGENTS hierarchy and HANDOFF instead of appending to accumulated files. Use for "restart", "AGENTS 완전 재설정", "AGENTS 다시 작성", "메모리 초기화", "메모리 재구성", "rebuild agents", and "rebuild project memory".
---

# Restart Project Memory

Rebuild agent memory from current evidence. This replaces accumulated memory; it does not append to it or reset source code.

## Workflow

1. Read the conversation; every root and nested AGENTS, AGENTS.override, CLAUDE, and HANDOFF file; canonical project documents; and enough current code, config, tests, and hooks to verify candidates.
2. Resolve conflicts in this order: current user decisions, current config and tests, current repository state, then git history. Existing memory is evidence to verify, not authority merely because it exists.
3. Read `references/routing.md` and inventory every item before writing:
   - Evidenced mandatory behavior → root or narrowest nested AGENTS
   - Feature and product decisions → scoped planning documents
   - Architecture and implementation knowledge → scoped development documents
   - Exact commands and recovery procedures → scoped operations documents
   - Cross-project preference → global memory
   - Immediate continuation → HANDOFF
   - Stale, duplicated, generated, or volatile narration → remove
4. Recreate each AGENTS file from verified rules only. Move rules to the narrowest valid scope and remove obsolete scopes or overrides that have no distinct role.
5. Preserve Claude-only instructions while repairing effective AGENTS imports. Keep tracked repository-owned files tracked; require separate evidence before treating a repository as external.
6. Rewrite scoped durable documents by meaning, without a generic memory dump, then rewrite HANDOFF from the current continuation only.
7. Run the shared auditor and fix every violation:

```bash
python3 <restart-skill-directory>/scripts/audit.py --root . --mode full
```

The auditor checks mechanical boundaries; manually verify every promoted rule against the seven-condition gate.

## Report

Report the audit total, rebuilt scopes, promoted rules with evidence, moved items with destinations, and entries retained because verification was incomplete. Quote every deleted pre-existing line verbatim because local memory may not have git recovery. Do not mention this skill or its version.

## References

- `references/routing.md` — promotion gate and destinations
- `references/templates.md` — rebuilt file shapes
- `references/edge-cases.md` — ownership, overrides, gitignore, and ambiguous targets
