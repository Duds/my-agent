# Operating Principles

These principles guide the development and operation of **MyAgent**, ensuring every technical decision aligns with our core mission of technological sovereignty.

## 1. Local-First, Cloud-Optional
- **Default to Local**: AI operations should run on local hardware (Ollama/M1 Mac) by default.
- **Strategic Cloud**: External APIs (Anthropic, Moonshot) are used only for high-complexity reasoning or when speed is a critical requirement for non-sensitive tasks.
- **Circuit Breaking**: If an API is unavailable or security risk is high, the system must degrade gracefully to local models.

## 2. Principle of Least Privilege (AI)
- **Data Isolation**: Sensitive data (NSFW, Personal, Financial) is strictly "trapped" within the local environment.
- **Minimal Exposure**: Only the specific context needed for a task is sent to external APIs.
- **Auditability**: Every external call is logged and can be audited for privacy compliance.

## 3. Trust but Verify (Multimodal Security)
- **Peer Review**: A local "Judge" model (e.g., Llama 3) must inspect outputs from more powerful but less trusted models for potential prompt injections or data leaks.
- **Validation Layers**: Use heuristic and AI-driven filters to prevent malicious command execution.

## 4. Neuro-Affirmative Design
- **Cognitive Load Reduction**: Automate repetitive tasks ("the boring stuff") to preserve executive function.
- **Compassionate Feedback**: The agent's tone should be supportive, acknowledging the difficulties of neurodivergence without being patronizing.
- **Bridge the Execution Gap**: Provide actionable next steps and micro-task breakdowns.

## 5. Vendor Independence
- **Portability**: All core logic must be written in standard Python, avoiding vendor-specific lock-in.
- **Adapter Pattern**: Use interchangeable adapters for all external services (LLMs, APIs, Tools).
- **Self-Hosting**: The long-term goal is a system that can be fully self-hosted without reliance on any single proprietary service.
