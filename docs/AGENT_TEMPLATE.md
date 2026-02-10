# Agent Template for LLM-Generated Agents

All custom agents must inherit from `AgentTemplate` and use `AgentContext` to access platform capabilities.

## Required Structure

```python
from core.agent_template import AgentTemplate
from core.agent_context import AgentContext

class MyAgent(AgentTemplate):
    async def run(self, ctx: AgentContext) -> dict:
        """Execute the agent logic. Use ctx.call_skill, ctx.call_mcp, ctx.use_capability."""
        # Example: call web search
        result = await ctx.call_skill("web-search", query="weather Sydney")
        return {"status": "ok", "data": result}

    def get_info(self) -> dict:
        """Return agent metadata for registration."""
        return {
            "id": "my-agent",
            "name": "My Agent",
            "description": "Does something useful",
            "skillIds": ["web-search"],
            "mcpServerIds": [],
            "capabilityIds": [],
        }
```

## Context API

- `ctx.call_skill(skill_id, **kwargs)` — Invoke a skill (e.g. `web-search`, `code-exec`, `file-ops`).
- `ctx.call_mcp(mcp_id, tool_name, **kwargs)` — Invoke an MCP server tool (e.g. `filesystem`, `github`).
- `ctx.use_capability(capability_id, **kwargs)` — Use a platform capability.

## Available Skills

- `web-search`: Search the web for real-time information.
- `code-exec`: Execute code in a sandboxed environment.
- `file-ops`: Read, write, and manage files.

## Available MCP Servers

- `filesystem`: Local filesystem access.
- `github`: GitHub repository operations.

## Rules

- Only use allowed imports (see `data/agent_rules.json`).
- No `eval`, `exec`, `subprocess`, `os.system`, or file system deletion.
- Always inherit from `AgentTemplate` and implement `run` and `get_info`.
