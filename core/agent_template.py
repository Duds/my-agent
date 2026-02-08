"""
AgentTemplate: Base class for custom agents.

All LLM-generated agents must inherit from AgentTemplate and implement
run(ctx: AgentContext) and get_info(). The framework uses this interface
to load, validate, and execute agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from core.agent_context import AgentContext


class AgentTemplate(ABC):
    """
    Base class for custom agents.

    Agents receive an AgentContext in run() and use it to call skills,
    MCPs, and capabilities. They must implement get_info() for metadata.
    """

    @abstractmethod
    async def run(self, ctx: AgentContext) -> Any:
        """
        Execute the agent's main logic.

        Args:
            ctx: AgentContext providing call_skill, call_mcp, use_capability.

        Returns:
            Result of the agent's execution (format is agent-specific).
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Return agent metadata for registration and display.

        Returns:
            Dict with at least: id, name, description. May include
            model, status, type, skillIds, mcpServerIds, capabilityIds.
        """
        pass
