---
description: Governance workflow for feature additions
---
# Workflow: Feature Development Lifecycle

1. **Analyze Necessity**: Evaluate if the feature aligns with "Security-First" and "Privacy-Obsessed" values.
2. **Design**: Draft an implementation plan and technical architecture update.
3. **Implement**: Code the solution, ensuring separation between core logic and adapters.
4. **Assurance**: Run `tests/routing` and `tests/security` to ensure no regressions.
5. **Document**: Update the `walkthrough.md` and `task.md` to reflect the change.
6. **Governance Review**: Check against `.agent/rules/governance.md`.
