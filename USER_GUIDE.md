# User Guide

Welcome to **MyAgent**, your secure personal AI assistant. This guide explains how to interact with your agent and manage its features.

## 📱 Interacting with MyAgent

### 1. Telegram Bot (On-the-go)
The Telegram bot is your primary mobile interface. It is designed for quick tasks, reminders, and "second brain" capture.
- **Command Routing**: Just talk naturally. The agent automatically routes sensitive topics to your local hardware and complex questions to professional models.
- **Key Commands**:
  - `/start`: Initialize connectivity.
  - `/help`: List available commands and usage.
  - `/status`: Check if local models (Ollama) are active.
  - `/reset`: Clear conversation context and start fresh.
  - `/think [brief|deep]`: Set thinking level (brief for quick responses, deep for thorough reasoning when supported).
  - `/setmychat`: Designate this chat for proactive messages.
  - `private: [text]`: Force local-only routing for a specific message.

### 2. CLI (Terminal & Scripting)
Run queries and send messages from the command line:
- `python -m scripts query "Your question"` – Submit a query and print the answer.
- `python -m scripts send "Your message"` – Send a message to your primary Telegram chat.
- `python -m scripts doctor` – Run health and config checks.

Set `MYAGENT_API_URL` (default: http://localhost:8001) and `MYAGENT_API_KEY` if the backend requires authentication. Use `--url` to override the base URL.

### 3. Web Dashboard (Deep Work)
Accessible via `http://localhost:3000` when running locally.
- **Task Management**: Visual interface for complex task breakdowns.
- **Settings**: Configure your API keys for Anthropic/Moonshot and select your preferred local models.
- **Logs**: View the routing decisions made by the agent (e.g., "Why did this go to Llama 3 instead of Claude?").

## 🔒 Privacy & Security

### How your data is handled
MyAgent uses a "Trapping" model:
1. **Classification**: Before anything happens, a local model classifies the "Intent" of your message.
2. **Local Isolation**: If your message is detected as personal or sensitive (passwords, health, NSFW), it is processed **entirely on your Mac**. It never leaves your network.
3. **Redaction**: For general tasks sent to the cloud, the agent attempts to redact PII (Personally Identifiable Information) before transmission.

## 🧠 Neuro-Supportive Features

MyAgent is built to support AuDHD workflows:
- **Micro-Tasking**: If you ask "How do I clean my room?", the agent won't just say "Clean it." It will provide a step-by-step list starting with something small like "Pick up 3 blue things."
- **Body Doubling**: Use the Telegram chat to "check-in" while working on tasks to stay on track.
- **Executive Function Support**: The agent manages your schedule and reminders to reduce the "mental gymnastics" of daily planning.

## 🛠 Troubleshooting

- **"Ollama not found"**: Ensure `ollama serve` is running in your terminal.
- **Slow Responses**: If you are in a low-power mode, the local models might take longer. Check Activity Monitor to see your Mac's resource usage.
- **API Errors**: Ensure your `.env` file contains valid keys for cloud providers.
```
