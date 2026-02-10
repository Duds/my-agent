"""Tests for agent generator."""

from unittest.mock import AsyncMock

import pytest

from core.agent_generator import (
    _extract_python_code,
    _extract_metadata_from_code,
    _extract_agent_id_and_name,
    _slugify,
    generate_and_register_agent,
)
from core.agent_validator import validate_agent_code


def test_extract_python_code_from_markdown():
    """Extract Python from ```python ... ``` block."""
    response = '''Here is the code:

```python
class Foo(AgentTemplate):
    pass
```
'''
    code = _extract_python_code(response)
    assert code is not None
    assert "class Foo" in code
    assert "AgentTemplate" in code


def test_extract_python_code_plain_block():
    """Extract from ``` ... ``` block without language."""
    response = '''
``` 
class Bar(AgentTemplate):
    pass
```
'''
    code = _extract_python_code(response)
    assert code is not None
    assert "class Bar" in code


def test_extract_python_code_no_block():
    """Return None when no code block."""
    response = "Just some text without code."
    assert _extract_python_code(response) is None


def test_extract_metadata_from_code():
    """Extract skillIds and mcpServerIds from ctx.call_skill/call_mcp."""
    code = '''
class MyAgent(AgentTemplate):
    async def run(self, ctx):
        await ctx.call_skill("web-search", query="x")
        await ctx.call_mcp("filesystem", "read_file", path="/tmp/x")
    def get_info(self):
        return {"id": "my-agent", "name": "My Agent"}
'''
    skill_ids, mcp_ids = _extract_metadata_from_code(code)
    assert "web-search" in skill_ids
    assert "filesystem" in mcp_ids


def test_extract_agent_id_and_name():
    """Extract id and name from get_info return."""
    code = '''
class WeatherAgent(AgentTemplate):
    async def run(self, ctx):
        pass
    def get_info(self):
        return {"id": "weather-agent", "name": "Weather Agent", "description": "Fetches weather"}
'''
    agent_id, agent_name = _extract_agent_id_and_name(code)
    assert agent_id == "weather-agent"
    assert agent_name == "Weather Agent"


def test_slugify():
    """Convert text to filesystem-safe slug."""
    assert _slugify("Weather Agent") == "weather-agent"
    assert _slugify("BOM Forecast") == "bom-forecast"
    assert _slugify("my_agent") == "my-agent"


def test_validate_agent_code_valid():
    """Valid agent code passes validation."""
    code = '''
from core.agent_template import AgentTemplate
from core.agent_context import AgentContext

class ValidAgent(AgentTemplate):
    async def run(self, ctx: AgentContext):
        return await ctx.call_skill("web-search", query="test")
    def get_info(self):
        return {"id": "valid", "name": "Valid", "skillIds": ["web-search"]}
'''
    is_valid, errors = validate_agent_code(code)
    assert is_valid, errors


def test_validate_agent_code_forbidden_pattern():
    """Code with eval fails validation."""
    code = '''
from core.agent_template import AgentTemplate
eval("bad")
'''
    is_valid, errors = validate_agent_code(code)
    assert not is_valid
    assert any("Forbidden" in e for e in errors)


@pytest.mark.asyncio
async def test_generate_and_register_agent_no_code_block():
    """When LLM returns no code block, returns failure."""
    mock_adapter = AsyncMock()
    mock_adapter.generate = AsyncMock(return_value="I cannot generate code for that.")
    success, message, entry = await generate_and_register_agent("make a weather agent", mock_adapter)
    assert success is False
    assert "extract" in message.lower() or "code" in message.lower()
    assert entry is None


@pytest.mark.asyncio
async def test_generate_and_register_agent_validation_fails():
    """When LLM returns code that fails validation, returns failure."""
    mock_adapter = AsyncMock()
    mock_adapter.generate = AsyncMock(
        return_value="```python\nfrom core.agent_template import AgentTemplate\neval('bad')\n```"
    )
    success, message, metadata = await generate_and_register_agent("make a bad agent", mock_adapter)
    assert success is False
    assert "validation" in message.lower() or "Forbidden" in message or "did not pass" in message
    assert metadata is not None and metadata.get("valid") is False
