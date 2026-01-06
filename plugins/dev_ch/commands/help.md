---
description: List all available commands in this plugin
---

# BCH Plugin - Available Commands

Display the following command list to the user:

## Agent Commands

| Command | Description | Agent |
|---------|-------------|-------|
| `/bch:review [context]` | Comprehensive code review | senior-code-reviewer |
| `/bch:portfolio` | Create/update project portfolio | portfolio-writer |
| `/bch:readme` | Create/improve README.md | readme-architect |
| `/bch:worklog` | Generate executive work logs | daily-work-writer |
| `/bch:devlog` | Generate detailed technical logs | daily-work-details-writer |
| `/bch:advisor` | Strategic project analysis | product-advisor |
| `/bch:update-stack [tech]` | Update technology stack | stack-updater |
| `/bch:blog [주제] [URL] [format]` | Write technical blog post | blog-writer |

## Utility Commands

| Command | Description |
|---------|-------------|
| `/bch:help` | Show this help message |
| `/bch:config` | Show current configuration |
| `/bch:config-set [key] [value]` | Update configuration |

## Configuration Keys

| Key | Description | Default |
|-----|-------------|---------|
| `obsidian_base` | Base path for Obsidian vault | `/home/bch/obsidian_sync` |
| `worklog_path` | Path for daily work logs | `docs/daily_work` |
| `devlog_path` | Path for detailed dev logs | `docs/daily_work_details` |
| `portfolio_path` | Path for portfolio files | `docs/portfolio` |
| `blog_path` | Path for blog posts | `docs/blog` |

## Skills (Auto-invoked)

- **commit**: Git commit best practices (automatically applied during commits)

## MCP Servers

- **playwright**: Browser automation
- **context7**: Documentation lookup
- **mcp-obsidian**: Obsidian vault integration

---
$ARGUMENTS
