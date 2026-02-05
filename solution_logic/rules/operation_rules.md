# Project Rules: Secure Personal Agentic Platform

These rules are enforced by the agentic system during its own evolution and operation.

## 1. Security & Privacy
- **Rule 1.1**: NEVER log PII in plaintext. All sensitive logs must be redacted or encrypted.
- **Rule 1.2**: ALWAYS require human-in-the-loop (HITL) for financial transactions and system-level file deletions.
- **Rule 1.3**: NEVER send local Home directory file paths or contents to external APIs unless specifically authorized by the user for that session.
- **Rule 1.4**: ALWAYS maintain an air-gapped logic for NSFW/Private roleplay; it resides ONLY in local model memory and temporary local files.

## 2. Architectural Integrity
- **Rule 2.1**: The Model Choice Engine MUST prioritize local models for requests categorized as "Private" or "Sensitive."
- **Rule 2.2**: All external API calls must be wrapped in a cost-monitoring utility.
- **Rule 2.3**: System memory must be stored in open, human-readable formats (e.g., Markdown for long-term, JSON for short-term).

## 3. Interaction Standards
- **Rule 3.1**: Telegram responses must be concise and actionable.
- **Rule 3.2**: Web UI is the primary source of truth for configuration and deep analytical reports.
- **Rule 3.3**: The agent must provide a "Daily Briefing" via Telegram every morning at 8:00 AM.
