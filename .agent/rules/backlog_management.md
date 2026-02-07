# Backlog Management Rules

To ensure a clean alignment between high-level vision and technical execution, **MyAgent** uses a "Backlog-as-Code" approach.

### 1. Hierarchy of Truth
1. **[VISION.md](../../VISION.md)**: The ultimate "Why".
2. **[TODO.md](../../TODO.md)**: The high-level Roadmap with MoSCoW priorities.
3. **[.agent/backlog/](./)**: Granular Product Backlog Items (PBIs) for technical breakdown.

### 2. PBI Lifecycle
- **Creation**: When a "Must Have" item in `TODO.md` is ready for technical design, a PBI file is created in `backlog/`.
- **Naming Convention**: `PBI-[SECTION_CODE]-[Feature-Name].md` (e.g., `PBI-SR-Skills-Registry.md`).
- **Completion**: Once a PBI is fully implemented, it is moved to a `backlog/archive/` folder or marked as completed within the file.

### 3. PBI Structure
Each PBI should follow this template:
- **Goal**: Clear statement of what success looks like.
- **MoSCoW Level**: Inherited from `TODO.md`.
- **Technical Breakdown**: List of specific files to create/modify.
- **Security Considerations**: "Trust but Verify" implications.
- **Definition of Done**: Specific verification steps (automated or manual).

### 4. Agent Interaction
When the agent starts a new task, it must:
1. Check `TODO.md` for priority.
2. Read any relevant `PBI-*.json` in `backlog/` for technical context.
3. Use the `Definition of Done` as the basis for the `walkthrough.md`.
