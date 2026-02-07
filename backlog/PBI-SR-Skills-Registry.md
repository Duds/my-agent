# PBI-SR: Skills Registry

**Goal**: Implement a central management system to register, discover, and invoke agent capabilities ("Skills").

**MoSCoW Level**: **Must Have (M)**

## 🛠 Technical Breakdown
- [ ] **Core Registry** (`core/skills.py`):
    - Create a `SkillRegistry` class (Singleton).
    - Implement `register_skill(name, func, description, schema)`.
    - Implement `get_skill(name)`.
- [ ] **Skill Decorator**:
    - Create a `@skill` decorator to easily register Python functions as agent tools.
- [ ] **Integration with Router** (`core/router.py`):
    - Allow the Router to query the `SkillRegistry` during intent classification.
- [ ] **Metadata**:
    - Ensure skills report their security level (Local Only vs. Remote Allowed).

## 🔒 Security Considerations
- **Isolation**: Skills should not have side effects outside their designated scope.
- **Verification**: The "Judge" model must be able to audit the input/output schema of any registered skill.
- **Privacy**: Local-only skills must be flagged to prevent accidental data leaks to remote LLMs.

## ✅ Definition of Done
1. [ ] `SkillRegistry` unit tests pass.
2. [ ] A sample skill (e.g., `get_system_time`) is successfully registered via decorator.
3. [ ] The `ModelRouter` can programmatically list all available skills.
4. [ ] Documentation updated in `ARCHITECTURE.md`.
