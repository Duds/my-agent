# Week 1 MVP: Telegram Bot Setup Guide

## 🚀 Quick Start

### 1. Get Your Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name for your bot (e.g., "MyAgent Personal Assistant")
   - Choose a username (must end in 'bot', e.g., "myagent_personal_bot")
4. Copy the API token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Paste it into `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2. Start the Telegram Bot

```bash
# Make sure Ollama is running
ollama serve

# In another terminal, start the bot
source venv/bin/activate
PYTHONPATH=. python3 core/telegram_bot.py
```

### 3. Test Your Bot

1. Open Telegram
2. Search for your bot's username
3. Send `/start` to begin
4. Try these test messages:
   - "Help me with a private matter" → Routes to hermes-roleplay (local)
   - "Write a Python function" → Routes to codellama
   - "Quick question about weather" → Routes to fast model (mistral)

## ✨ Features

### Fast Presence Model
- **Instant acknowledgment** (<500ms) with mistral
- Keeps you engaged while slow models process
- Example flow:
  1. You: "Analyze this financial data..."
  2. Bot (instant): "⚡ I'll analyze that financial data for you..."
  3. Bot (typing indicator shows)
  4. Bot (after processing): "🎯 Routing: finance → anthropic"
  5. Bot (final response): "✅ Processed with anthropic..."

### Intelligent Routing
The bot automatically detects intent and routes to the best model:
- 🔒 **Private/NSFW** → hermes-roleplay (local, never logged)
- 💻 **Coding** → codellama or anthropic
- 💰 **Finance** → anthropic (manual approval coming soon)
- ⚡ **Speed** → mistral (fast local)
- 🎯 **Quality** → anthropic (complex reasoning)

## 🔧 Troubleshooting

### Bot doesn't respond
- Check that `ollama serve` is running
- Verify `TELEGRAM_BOT_TOKEN` in `.env` is correct
- Check logs for errors

### Slow responses
- Ensure models are pulled: `ollama list`
- Check system resources (Mac Mini M1 with 8GB RAM)
- Fast presence should still acknowledge instantly

### "Model not found" errors
Pull missing models:
```bash
ollama pull llama3
ollama pull mistral
ollama pull hermes-roleplay
ollama pull codellama-instruct
```

## 📝 Next Steps

After testing the basic bot:
1. Add Anthropic API key for quality responses
2. Implement full model responses (not just routing info)
3. Add session management (separate Telegram from Web UI)
4. Implement manual approval for finance operations
5. Add typing indicators during slow processing

---

**Status:** Ready to test! 🎉
