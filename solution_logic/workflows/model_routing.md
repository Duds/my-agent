---
description: How to switch models based on intent
---
# Workflow: Model Choice Engine Logic

1. **Analyze Intent**: Receive user request and determine classification (Speed, Quality, Private, NSFW).
2. **Check Context**: Determine if the request requires Google Workspace or Home Directory access.
3. **Select Model**:
    - If **NSFW/Private**: Route to `Local-Llama-3-8B-Q4`.
    - If **Speed/Utility**: Route to `Local-Mistral-7B` or `Moonshot-v1-8k`.
    - If **Coding/Reasoning**: Route to `Claude-3.5-Sonnet`.
    - If **Financial/Strategic**: Route to `Claude-3.5-Opus` (if available) or `Sonnet`.
4. **Execute & Verify**: Send prompt, receive output, and have a "Judge" model (Local) verify for security threats if the output contains executable code or sensitive links.
5. **Report Cost**: Log the token usage and cost for the transaction.
