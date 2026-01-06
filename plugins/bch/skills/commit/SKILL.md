---
name: commit
description: Git commit best practices and guidelines. Automatically applied when creating commits to ensure logical atomicity and result-oriented messages.
---

# Git Commit Strategy

## 1. Commit Scope (Logical Atomicity)

**MUST FOLLOW:** Do not commit per file. Commit per **feature unit**.

- **Principle:** If you modified `main.py`, `utils.py`, `config.yaml` to develop Feature A, these 3 files **MUST be in a single commit**.
- **Reason:** When reverting to a specific commit, that feature should work completely.

## 2. Commit Message Rules (Result-Oriented)

**MUST FOLLOW:** Do not write conversation history (process). Write only the **final code changes (result)**.

- **Background:** Even if there were 10 modifications during development (error fixes, typo fixes, etc.), the commit message should only state the finally implemented feature.
- **Guidelines:**
  - ❌ "Fixed typo, fixed A function error, added library to implement login feature" (NO process listing)
  - ✅ "feat(auth): Implement JWT-based login" (Only final result)

## 3. Commit Prefixes

| Prefix | Usage |
|--------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Code formatting (no functional change) |
| `refactor` | Code refactoring |
| `test` | Test code |
| `chore` | Build, config files, etc. |

## 4. Pre-Commit Checklist

Before creating a commit, ask yourself:

1. **Are all related files included?** (Are all dependency files modified for the feature `git add`ed?)
2. **Is the message clean?** (Does it contain only the core implementation without repetitive "fix", "modify"?)
3. **Is it the diff from previous commit?** (Did you summarize `git diff` content, not conversation log?)

## 5. Examples

### Scenario: Created `search.py` and modified `api.py` for search feature, fixed 3 errors during development

**❌ Bad Example (NEVER DO THIS)**

```bash
git add search.py
git commit -m "feat: Create search module"
git add api.py
git commit -m "fix: Fix api connection and variable name errors and import errors"
```

**✅ Good Example (RECOMMENDED)**

```bash
# Add all related files at once
git add search.py api.py

# Skip the process, only state the finally implemented feature
git commit -m "feat(search): Implement keyword search and connect API endpoint"
```

## 6. HEREDOC Format for Commit Messages

Always use HEREDOC for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
feat(scope): Brief description

- Detail 1
- Detail 2
EOF
)"
```
