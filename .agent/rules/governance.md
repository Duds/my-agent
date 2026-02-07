# Project Governance Rules (Antigravity)

These rules govern the development, maintenance, and continuous improvement of the Secure Personal Agentic Platform.

## 1. Development Principles
- **Governance 1.1**: All code changes must be auditable and clearly documented in the project walkthrough.
- **Governance 1.2**: New features must include automated verification tests before completion.
- **Governance 1.3**: The technology stack (Python, FastAPI, Next.js) must be maintained for maximum portability and vendor independence.

## 2. Security & Assurance
- **Governance 2.1**: Security guardrails (Model Peer-Review) must be verified after any routing logic changes.
- **Governance 2.2**: API keys and secrets must never be hardcoded; use `.env` files and environment variables.
- **Governance 2.3**: Periodic "threat modeling" reviews should be conducted as the agent's capabilities expand.

## 3. Continuous Improvement
- **Governance 3.1**: The solution must be regularly evaluated against the Operating Principles and Values.
- **Governance 3.2**: Refactoring should prioritize reducing technical debt and improving local model performance on the Mac Mini M1.
