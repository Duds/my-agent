# Slack Channel Setup (PBI-045)

The Slack adapter lets you use MyAgent from Slack. Inbound messages are routed through the same Router and security stack as Telegram.

## Prerequisites

- Backend running (e.g. `PYTHONPATH=. python3 -m core.main`) with a **public URL** for Slack to send events (e.g. ngrok for local dev).
- Slack app with Bot Token and Signing Secret.

## 1. Create a Slack app

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and **Create New App** → **From scratch**.
2. Name the app (e.g. "MyAgent") and pick a workspace.
3. Under **OAuth & Permissions**, add Bot Token Scopes: `chat:write`, `app_mentions:read`, `channels:history`, `groups:history`, `im:history` (as needed for where the bot will run).
4. Install the app to the workspace and copy the **Bot User OAuth Token** (starts with `xoxb-`).
5. Under **Basic Information**, copy the **Signing Secret**.

## 2. Configure environment

In `.env`:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
```

## 3. Request URL (Events API)

1. In the Slack app, go to **Event Subscriptions** and turn **Enable Events** On.
2. Set **Request URL** to your backend URL plus path: `https://your-domain.com/api/channels/slack/events`.
3. Slack will send a `url_verification` challenge; the backend responds with the challenge so the URL is verified.
4. Under **Subscribe to bot events**, add **message.channels** (and/or **message.im**, **message.groups** if you want DMs and private channels). Save changes.

## 4. Invite the bot

In Slack, invite the app to the channel: `/invite @YourBotName`.

## Behaviour

- Messages posted in channels (or DMs) where the bot is present are sent to the backend.
- The backend routes the message through the same intent-based Router as Telegram and posts the reply back to the same channel (or thread).
- No API key is required for the Events endpoint; requests are verified using the Slack signing secret.

## Troubleshooting

- **Invalid Slack signature**: Ensure `SLACK_SIGNING_SECRET` matches the value in the Slack app and that the request body is not modified (use raw body for verification).
- **No reply**: Check backend logs; ensure the bot has `chat:write` and is in the channel.
- **Local development**: Use a tunnel (e.g. ngrok) and set the Request URL to `https://your-ngrok-url.ngrok.io/api/channels/slack/events`.
