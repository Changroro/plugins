---
name: find-me
description: ALWAYS use, unasked, in every project, whenever a user message reveals anything about the user — even one clause said in passing before a technical request. Record it first, then do the task. Covers habits, routines, feelings, worries, self-esteem, comparisons with others, career plans, values, likes and dislikes, relationships, background, experiences, achievements, and how they work or use AI. Appends concise, contextual summaries to a dated Obsidian log — raw material for cover letters.
---

# Find Me

Keep a running record of what the user says about themselves, as self-contained summaries that remain understandable later, so cover letters and self-analysis start from facts instead of guesses.

## What counts

- Any statement the user makes about themselves, including one said in passing inside a technical request.
- Not project facts, task requests, or your own observations about the user. Record only what the user said.

## Where

- Find the vault in the Obsidian registry: `~/.config/obsidian/obsidian.json` on Linux, `~/Library/Application Support/obsidian/obsidian.json` on macOS. The target is the one registered vault that has a `개인/` folder.
- No match or more than one: reply `find-me: 볼트를 찾지 못함` and stop. Never guess a path or create a vault.
- File: `<vault>/개인/나에 대해/기록.md`. If it is missing, create it with this header:

```markdown
---
title: 나에 대해
tags:
  - 자소서소재
---

# 나에 대해
```

## Entry format

Append at the end of the file. Add a `## YYYY-MM-DD` heading (local date) first if the file's last date heading is not today.

```markdown
- #습관 사용자의 습관과 이를 말한 맥락을 한두 문장으로 정리한다.
```

- Tags, one or two: `#습관` `#성격` `#가치관` `#감정` `#고민` `#관계` `#경험` `#성과` `#일하는방식` `#취향`
- Summarize the user's meaning in clear, standalone Korean. Include the context needed to understand it later, merge repeated points from the same conversation, and preserve uncertainty, feelings, and distinctions between what the user did and what an agent did. Do not infer, rate, or diagnose.
- Skip a point already recorded under today's heading.

## Rules

- Append new entries with a shell `>>` heredoc so concurrent sessions do not overwrite each other. Do not change older entries unless the user explicitly asks to revise them. A changed view is a new entry on the day it was said.
- Leave out passwords, tokens, keys, contact details, ID numbers, and addresses. Replace other people's names with a role (친구, 동료, 팀장).
- Do not interrupt the current task. After writing, include `find-me: 기록함 → 개인/나에 대해/기록.md` in your reply, followed by the newly appended summaries exactly as saved.
- Never commit; the vault's own backup handles git.
