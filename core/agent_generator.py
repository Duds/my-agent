"""
AgentGenerator: Generates custom agent code from natural language.

Invokes LLM with agent_rules, AGENT_TEMPLATE, available skills/MCPs, and user request.
Validates generated code, writes to agents/, and registers in data/agents.json.
"""

import ast
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .agent_validator import validate_agent_code
from .config import settings

logger = logging.getLogger(__name__)


def _load_agent_template_doc() -> str:
    """Load AGENT_TEMPLATE.md for LLM context."""
    root = Path(__file__).resolve().parent.parent
    path = root / "docs" / "AGENT_TEMPLATE.md"
    if path.exists():
        return path.read_text()
    return "See core.agent_template and core.agent_context for the required interface."


def _load_agent_rules() -> str:
    """Load agent rules as string for LLM context."""
    root = Path(__file__).resolve().parent.parent
    path = root / "data" / "agent_rules.json"
    if path.exists():
        with open(path) as f:
            rules = json.load(f)
        return json.dumps(rules, indent=2)
    return "{}"


def _get_available_skills() -> List[Dict[str, Any]]:
    """Get list of available skills (from main app state or config)."""
    try:
        from core.main import _skills_store
        return [s for s in (_skills_store or []) if s.get("enabled", True)]
    except Exception:
        return [
            {"id": "web-search", "name": "Web Search", "description": "Search the web"},
            {"id": "code-exec", "name": "Code Execution", "description": "Execute code in sandbox"},
            {"id": "file-ops", "name": "File Operations", "description": "Read/write files"},
        ]


def _get_available_mcps() -> List[Dict[str, Any]]:
    """Get list of available MCP servers."""
    try:
        from core.main import _load_mcp_servers
        return _load_mcp_servers()
    except Exception:
        return [
            {"id": "filesystem", "name": "Filesystem", "description": "Local filesystem"},
            {"id": "github", "name": "GitHub", "description": "GitHub operations"},
        ]


def _extract_python_code(response: str) -> Optional[str]:
    """Extract Python code block from LLM response."""
    # Try ```python ... ``` or ``` ... ```
    for pattern in [
        r"```python\s*(.*?)\s*```",
        r"```\s*(.*?)\s*```",
    ]:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    # No code block; treat entire response as code if it looks like Python
    if "class " in response and "AgentTemplate" in response:
        return response.strip()
    return None


def _extract_metadata_from_code(code: str) -> Tuple[List[str], List[str]]:
    """Extract skillIds and mcpServerIds from generated code by parsing ctx.call_skill/call_mcp."""
    skill_ids: List[str] = []
    mcp_ids: List[str] = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Await):
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    if isinstance(func, ast.Attribute):
                        if func.attr == "call_skill" and node.value.args:
                            arg = node.value.args[0]
                            if isinstance(arg, ast.Constant):
                                skill_ids.append(arg.value)
                        elif func.attr == "call_mcp" and node.value.args:
                            arg = node.value.args[0]
                            if isinstance(arg, ast.Constant):
                                mcp_ids.append(arg.value)
    except Exception:
        pass
    return list(dict.fromkeys(skill_ids)), list(dict.fromkeys(mcp_ids))


def _extract_agent_id_and_name(code: str) -> Tuple[str, str]:
    """Extract id and name from get_info() return in code, or use defaults."""
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "get_info":
                        for n in ast.walk(item):
                            if isinstance(n, ast.Return) and n.value and isinstance(n.value, ast.Dict):
                                keys = [k.value for k in n.value.keys if isinstance(k, ast.Constant)]
                                values = n.value.values
                                info = dict(zip(keys, values))
                                id_val = info.get("id")
                                name_val = info.get("name")
                                agent_id = id_val.value if isinstance(id_val, ast.Constant) else "generated-agent"
                                agent_name = name_val.value if isinstance(name_val, ast.Constant) else "Generated Agent"
                                return agent_id, agent_name
    except Exception:
        pass
    return "generated-agent", "Generated Agent"


def _slugify(text: str) -> str:
    """Convert to filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "agent"


async def generate_and_register_agent(
    user_request: str,
    adapter: Any,
    model_override: Optional[str] = None,
    dry_run: bool = False,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Generate agent code from user request, validate, and optionally register.

    Args:
        user_request: Natural language request (e.g. "create an agent to fetch weather from BOM").
        adapter: ModelAdapter to use for LLM generation.
        model_override: Optional model override for the adapter.
        dry_run: If True, validate and return code + metadata but do not write files or update agents.json.

    Returns:
        Tuple of (success, message, metadata or None).
        On success with dry_run=True: metadata includes code, agent_id, agent_name, valid (True), and optionally validation_errors.
        On success with dry_run=False: (True, "Agent 'X' created and registered.", entry).
        On failure: (False, error_message, metadata with valid=False and validation_errors if applicable).
    """
    template_doc = _load_agent_template_doc()
    rules_json = _load_agent_rules()
    skills = _get_available_skills()
    mcps = _get_available_mcps()

    skills_desc = ", ".join(f"{s['id']} ({s['description']})" for s in skills)
    mcps_desc = ", ".join(f"{m['id']} ({m['description']})" for m in mcps)

    prompt = f"""You are a code generator for a secure agent platform. Generate a Python agent class that fulfills the user's request.

## Rules (from agent_rules.json)
{rules_json}

## Template and Context API
{template_doc}

## Available Skills
{skills_desc}

## Available MCP Servers
{mcps_desc}

## User Request
{user_request}

## Instructions
1. Create a single class that inherits from AgentTemplate.
2. Implement async def run(self, ctx: AgentContext) using ctx.call_skill, ctx.call_mcp, or ctx.use_capability.
3. Implement def get_info(self) returning dict with: id, name, description, skillIds, mcpServerIds, capabilityIds.
4. Use only allowed imports. No eval, exec, subprocess, or file deletion.
5. Output ONLY the Python code, inside a ```python ... ``` block. No explanation before or after."""

    try:
        response = await adapter.generate(prompt, model_override=model_override)
    except Exception as e:
        logger.exception("LLM generation failed: %s", e)
        return False, f"Failed to generate agent: {e}", None

    code = _extract_python_code(response)
    if not code:
        return False, "Could not extract Python code from the response. Please try again.", None

    is_valid, errors = validate_agent_code(code)
    agent_id, agent_name = _extract_agent_id_and_name(code)
    skill_ids, mcp_ids = _extract_metadata_from_code(code)

    metadata = {
        "code": code,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "valid": is_valid,
        "validation_errors": errors if not is_valid else [],
    }

    if not is_valid:
        err_msg = "; ".join(errors)
        return False, f"Generated code did not pass validation: {err_msg}", metadata

    if dry_run:
        logger.info("Agent %s generated (dry run); not writing files.", agent_id)
        return True, f"Agent '{agent_name}' is ready for review. You can register it from the Review dialog.", metadata

    slug = _slugify(agent_id)
    agents_dir = Path(__file__).resolve().parent.parent / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    agent_path = agents_dir / f"{slug}.py"

    try:
        agent_path.write_text(code, encoding="utf-8")
    except Exception as e:
        logger.exception("Failed to write agent file: %s", e)
        return False, f"Failed to write agent file: {e}", metadata

    agents_config_path = Path(settings.agents_config_path)
    agents_config_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "id": agent_id,
        "name": agent_name,
        "status": "idle",
        "type": "internal",
        "model": "",
        "description": f"Generated from: {user_request[:80]}...",
        "source": f"agents/{slug}.py",
        "skillIds": skill_ids,
        "mcpServerIds": mcp_ids,
        "capabilityIds": [],
    }

    try:
        if agents_config_path.exists():
            with open(agents_config_path) as f:
                data = json.load(f)
        else:
            data = {"agents": []}
        data["agents"].append(entry)
        with open(agents_config_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.exception("Failed to register agent: %s", e)
        if agent_path.exists():
            agent_path.unlink()
        return False, f"Failed to register agent: {e}", metadata

    logger.info("Agent %s created and registered at %s", agent_id, agent_path)
    return True, f"Agent '{agent_name}' created and registered. It will appear in the Automation Hub.", entry


def register_agent_code(code: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate agent code and register it (write to agents/, update agents.json).
    Used by POST /api/agents/register when user approves from the Review UI.

    Returns:
        (True, entry, None) on success; (False, None, error_message) on validation or write failure.
    """
    is_valid, errors = validate_agent_code(code)
    if not is_valid:
        return False, None, "; ".join(errors)

    agent_id, agent_name = _extract_agent_id_and_name(code)
    skill_ids, mcp_ids = _extract_metadata_from_code(code)
    slug = _slugify(agent_id)
    agents_dir = Path(__file__).resolve().parent.parent / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    agent_path = agents_dir / f"{slug}.py"

    try:
        agent_path.write_text(code, encoding="utf-8")
    except Exception as e:
        logger.exception("Failed to write agent file: %s", e)
        return False, None, str(e)

    agents_config_path = Path(settings.agents_config_path)
    agents_config_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": agent_id,
        "name": agent_name,
        "status": "idle",
        "type": "internal",
        "model": "",
        "description": "Registered via Review UI",
        "source": f"agents/{slug}.py",
        "skillIds": skill_ids,
        "mcpServerIds": mcp_ids,
        "capabilityIds": [],
    }

    try:
        if agents_config_path.exists():
            with open(agents_config_path) as f:
                data = json.load(f)
        else:
            data = {"agents": []}
        data["agents"].append(entry)
        with open(agents_config_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.exception("Failed to register agent: %s", e)
        if agent_path.exists():
            agent_path.unlink()
        return False, None, str(e)

    logger.info("Agent %s registered at %s", agent_id, agent_path)
    return True, entry, None
