"""Tests for agent validator."""

import pytest

from core.agent_validator import validate_agent_code


def test_valid_agent_passes():
    """Valid agent with run and get_info passes."""
    code = """
from core.agent_template import AgentTemplate
from core.agent_context import AgentContext
from typing import Any, Dict

class BOMAgent(AgentTemplate):
    async def run(self, ctx: AgentContext) -> Any:
        return await ctx.call_skill("web-search", query="test")
    def get_info(self) -> Dict[str, Any]:
        return {"id": "bom", "name": "BOM", "description": "test"}
"""
    valid, errors = validate_agent_code(code)
    assert valid is True
    assert errors == []


def test_agent_without_base_class_fails():
    """Agent not inheriting from AgentTemplate fails."""
    code = """
class BadAgent:
    async def run(self, ctx):
        return 1
    def get_info(self):
        return {}
"""
    valid, errors = validate_agent_code(code)
    assert valid is False
    assert any("inherit" in e for e in errors)


def test_agent_with_eval_fails():
    """Agent using eval() fails."""
    code = """
from core.agent_template import AgentTemplate

class Bad(AgentTemplate):
    async def run(self, ctx):
        eval("1+1")
        return 1
    def get_info(self):
        return {}
"""
    valid, errors = validate_agent_code(code)
    assert valid is False
    assert any("eval" in e for e in errors)


def test_syntax_error_fails():
    """Invalid Python syntax fails."""
    code = "class Bad( missing colon"
    valid, errors = validate_agent_code(code)
    assert valid is False
    assert any("Syntax" in e for e in errors)


def test_agent_missing_get_info_fails():
    """Agent with run but no get_info fails."""
    code = """
from core.agent_template import AgentTemplate

class Incomplete(AgentTemplate):
    async def run(self, ctx):
        return 1
"""
    valid, errors = validate_agent_code(code)
    assert valid is False
    assert any("get_info" in e for e in errors)


def test_agent_forbidden_import_fails():
    """Agent with disallowed import fails."""
    code = """
import os
from core.agent_template import AgentTemplate

class Bad(AgentTemplate):
    async def run(self, ctx):
        return 1
    def get_info(self):
        return {}
"""
    valid, errors = validate_agent_code(code)
    assert valid is False
    assert any("Import" in e or "not allowed" in e for e in errors)
