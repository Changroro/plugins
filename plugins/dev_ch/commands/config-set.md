---
description: Update plugin configuration value
---

Update a configuration value in `${CLAUDE_PLUGIN_ROOT}/config.json`.

User input: $ARGUMENTS

Expected format: `key value`
Example: `obsidian_base /home/user/my_obsidian`

Valid keys:
- `obsidian_base`: Base path for Obsidian vault
- `worklog_path`: Relative path for daily work logs (from obsidian_base)
- `devlog_path`: Relative path for detailed dev logs (from obsidian_base)
- `portfolio_path`: Relative path for portfolio files (from obsidian_base)

Steps:
1. Parse the key and value from arguments
2. Read current config from `${CLAUDE_PLUGIN_ROOT}/config.json`
3. Update the specified key
4. Write back to config.json
5. Confirm the change to the user
