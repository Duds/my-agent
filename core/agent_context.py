"""
AgentContext: Injectable runtime context for custom agents.

Provides call_skill(), call_mcp(), and use_capability() so agents can invoke
platform Skills, MCP servers, and Capabilities. Enforces per-agent permissions
so agents only access what they are allowed to use.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentContext:
    """
    Runtime context injected into agents when they run.

    Agents receive this context and use it to call skills, MCPs, and capabilities.
    The context enforces that the agent only accesses allowed skillIds, mcpServerIds,
    and capabilityIds as defined in the agent's registry entry.
    """

    def __init__(
        self,
        agent_id: str,
        allowed_skill_ids: Optional[List[str]] = None,
        allowed_mcp_ids: Optional[List[str]] = None,
        allowed_capability_ids: Optional[List[str]] = None,
        skill_dispatcher: Optional[Any] = None,
        mcp_dispatcher: Optional[Any] = None,
        capability_dispatcher: Optional[Any] = None,
    ) -> None:
        self.agent_id = agent_id
        self._allowed_skills = set(allowed_skill_ids or [])
        self._allowed_mcps = set(allowed_mcp_ids or [])
        self._allowed_capabilities = set(allowed_capability_ids or [])
        self._skill_dispatcher = skill_dispatcher
        self._mcp_dispatcher = mcp_dispatcher
        self._capability_dispatcher = capability_dispatcher

    async def call_skill(self, skill_id: str, **kwargs: Any) -> Any:
        """
        Invoke a skill from the Skills Registry.

        Args:
            skill_id: ID of the skill (e.g. 'web-search', 'code-exec').
            **kwargs: Skill-specific parameters.

        Returns:
            Skill result (format depends on the skill).

        Raises:
            PermissionError: If this agent is not allowed to use this skill.
            ValueError: If skill_id is not found or not enabled.
        """
        if skill_id not in self._allowed_skills:
            raise PermissionError(
                f"Agent {self.agent_id} is not allowed to use skill '{skill_id}'. "
                f"Allowed: {sorted(self._allowed_skills)}"
            )
        if self._skill_dispatcher:
            return await self._skill_dispatcher.invoke(skill_id, **kwargs)
        logger.warning("Skill dispatcher not configured; call_skill(%s) would be a no-op", skill_id)
        return {"status": "unimplemented", "skill_id": skill_id}

    async def call_mcp(self, mcp_id: str, tool_name: str, **kwargs: Any) -> Any:
        """
        Invoke a tool on an MCP server.

        Args:
            mcp_id: ID of the MCP server (e.g. 'filesystem', 'github').
            tool_name: Name of the tool to invoke.
            **kwargs: Tool-specific parameters.

        Returns:
            Tool result (format depends on the MCP server).

        Raises:
            PermissionError: If this agent is not allowed to use this MCP.
        """
        if mcp_id not in self._allowed_mcps:
            raise PermissionError(
                f"Agent {self.agent_id} is not allowed to use MCP '{mcp_id}'. "
                f"Allowed: {sorted(self._allowed_mcps)}"
            )
        if self._mcp_dispatcher:
            return await self._mcp_dispatcher.invoke(mcp_id, tool_name, **kwargs)
        logger.warning("MCP dispatcher not configured; call_mcp(%s, %s) would be a no-op", mcp_id, tool_name)
        return {"status": "unimplemented", "mcp_id": mcp_id, "tool": tool_name}

    async def use_capability(self, capability_id: str, **kwargs: Any) -> Any:
        """
        Use a platform capability.

        Args:
            capability_id: ID of the capability (e.g. 'fetch_http', 'parse_html').
            **kwargs: Capability-specific parameters.

        Returns:
            Capability result.

        Raises:
            PermissionError: If this agent is not allowed to use this capability.
        """
        if capability_id not in self._allowed_capabilities:
            raise PermissionError(
                f"Agent {self.agent_id} is not allowed to use capability '{capability_id}'. "
                f"Allowed: {sorted(self._allowed_capabilities)}"
            )
        if self._capability_dispatcher:
            return await self._capability_dispatcher.invoke(capability_id, **kwargs)
        logger.warning("Capability dispatcher not configured; use_capability(%s) would be a no-op", capability_id)
        return {"status": "unimplemented", "capability_id": capability_id}
