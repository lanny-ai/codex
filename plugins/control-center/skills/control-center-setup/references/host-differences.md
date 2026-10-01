# Claude Code vs Codex

| Concern | Claude Code | Codex / ChatGPT desktop |
|---|---|---|
| Skill location | `~/.claude/skills/<name>/SKILL.md` (user) or `.claude/skills/` (project); plugins via marketplace | plugin `skills/` directory, installed from a marketplace |
| Invoke | `/skill-name` or natural language | `$skill-name` |
| MCP | `claude mcp add`, `.mcp.json`, managed connectors | app MCP settings |
| Secrets | OS keychain or git-ignored `.env` | same |
| Remote | Claude Code on the web / mobile, scheduled routines | Codex cloud tasks |
| Scheduling | Routines / cron / Task Scheduler | app scheduled tasks |

This plugin's skills are written to work under both. When a step is host-specific, ask which host the operator is in rather than guessing.
