"""
AgentValidator: Validates generated agent code against platform rules.

Performs AST-based checks and pattern matching to ensure generated code
conforms to security and structural requirements before registration.
"""

import ast
import json
import os
from pathlib import Path
from typing import List, Tuple


def _load_agent_rules() -> dict:
    """Load agent rules from config."""
    root = Path(__file__).resolve().parent.parent
    path = root / "data" / "agent_rules.json"
    if not path.exists():
        return {"allowed_imports": [], "forbidden_patterns": [], "required_interface": {}}
    with open(path) as f:
        return json.load(f)


def validate_agent_code(code: str) -> Tuple[bool, List[str]]:
    """
    Validate agent Python code against agent_rules.json.

    Args:
        code: Python source code of the agent.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors: List[str] = []

    # Parse AST
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]

    rules = _load_agent_rules()
    allowed_imports = set(rules.get("allowed_imports", []))
    forbidden_patterns = rules.get("forbidden_patterns", [])
    required = rules.get("required_interface", {})

    # Check forbidden patterns in raw source
    for pat in forbidden_patterns:
        if pat in code:
            errors.append(f"Forbidden pattern found: {pat!r}")

    def is_allowed_module(mod: str) -> bool:
        if not mod:
            return True
        return any(mod == a or mod.startswith(a + ".") for a in allowed_imports)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not is_allowed_module(alias.name):
                    errors.append(f"Import not allowed: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and not is_allowed_module(node.module):
                errors.append(f"Import from not allowed: {node.module}")

    # Check for required base class and methods
    base_class = required.get("base_class", "AgentTemplate")
    required_methods = set(required.get("required_methods", ["run", "get_info"]))
    found_base = False
    found_methods: set = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = (base.id if isinstance(base, ast.Name) else base.attr) if isinstance(base, (ast.Name, ast.Attribute)) else ""
                if base_name == base_class:
                    found_base = True
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            found_methods.add(item.name)
                    break

    if not found_base:
        errors.append(f"Agent must inherit from {base_class}")
    else:
        for method in required_methods:
            if method not in found_methods:
                errors.append(f"Agent must implement method: {method}")

    return len(errors) == 0, errors
