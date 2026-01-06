# cc-plugins-bch

Bae-ChangHyun's personal Claude Code plugins marketplace.

## Installation

```bash
# Add marketplace
/plugin marketplace add Bae-ChangHyun/cc-plugins-bch

# Install plugin
/plugin install bch@cc-plugins-bch
```

## Plugins

### bch

Personal Claude Code plugin with custom agents, skills, and MCP servers.

#### Agents

| Agent | Description |
|-------|-------------|
| `bch:blog-writer` | Write technical blog posts |
| `bch:daily-work-writer` | Generate daily work logs |
| `bch:daily-work-details-writer` | Generate detailed technical logs |
| `bch:portfolio-writer` | Create/update project portfolio |
| `bch:product-advisor` | Strategic project analysis |
| `bch:readme-architect` | Create/improve README.md |
| `bch:senior-code-reviewer` | Comprehensive code review |
| `bch:stack-updater` | Update technology stack |

#### Commands (Slash Commands)

| Command | Description |
|---------|-------------|
| `/bch:help` | List all available commands |
| `/bch:config` | Show current configuration |
| `/bch:config-set` | Update configuration |
| `/bch:review` | Launch code reviewer agent |
| `/bch:portfolio` | Launch portfolio writer agent |
| `/bch:readme` | Launch README architect agent |
| `/bch:worklog` | Generate work logs |
| `/bch:devlog` | Generate detailed technical logs |
| `/bch:advisor` | Launch product advisor agent |
| `/bch:update-stack` | Launch stack updater agent |
| `/bch:blog` | Write a technical blog post |

#### Skills

| Skill | Description |
|-------|-------------|
| `/bch:commit` | Git commit with best practices |

#### MCP Servers

- **playwright**: Browser automation
- **context7**: Up-to-date documentation lookup
- **mcp-obsidian**: Obsidian vault integration

## Configuration

Set environment variables before using:

```bash
export OBSIDIAN_BASE="/path/to/obsidian/vault"
export OBSIDIAN_API_KEY="your-api-key"
export BLOG_PATH="path/to/blog/folder"
```

## Update

```bash
/plugin marketplace update
/plugin update bch@cc-plugins-bch
```
