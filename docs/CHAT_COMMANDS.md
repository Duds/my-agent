# Chat Commands

This document defines the structured slash-style chat commands for MyAgent. These commands enable consistent behaviour across Telegram and future channel adapters.

## Command Set

| Command | Description | Usage |
|---------|-------------|-------|
| `/status` | Return session and model status (Ollama, backend) | `/status` |
| `/reset` | Clear conversation context and start fresh | `/reset` |
| `/think` | Set thinking level (brief or deep) | `/think [brief\|deep]` |
| `/start` | Welcome message and initial setup | `/start` |
| `/help` | List available commands | `/help` |
| `/setmychat` | Designate current chat for proactive messages | `/setmychat` |

## Behaviour

- **`/status`**: Returns compact status (e.g. Ollama online/offline, available models). No routing to LLM.
- **`/reset`**: Clears per-session context. User receives confirmation. Next message starts fresh.
- **`/think`**: Sets thinking level in session context. `brief` = quick responses (default); `deep` = more thorough reasoning when supported by the model.

## Implementation Notes for Channel Adapters

1. Detect leading `/` before routing to the model.
2. Parse command name and optional arguments.
3. Execute command handler or forward to backend if applicable.
4. Return structured response to user; do not route command text to the LLM.

The `GET /api/commands` endpoint returns the full command list for UI and documentation.
