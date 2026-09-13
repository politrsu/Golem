# Configuration

Example `config.json`:

```json
{
  "delivery": {
    "mode": "agent_chat",
    "destination": "current_conversation",
    "bot_token_env": "SANCTIONS_TELEGRAM_BOT_TOKEN",
    "queued_activation_policy": "review"
  },
  "database": "./runtime/sanctions.sqlite3",
  "output_directory": "./runtime/documents"
}
```

## New user without a dedicated channel

1. Installation leaves the scheduler disabled.
2. Select `agent_chat`. In an agent platform, bind it to the current primary conversation. In standalone Telegram mode, provide that private chat's numeric identifier.
3. Send a test message and verify delivery.
4. Enable the scheduler. New alerts and their DOCX files now arrive in the main agent chat.

## User with a dedicated channel

1. Create the Telegram channel manually.
2. Add the bot as an administrator and allow it to post messages.
3. Obtain the numeric channel identifier or use a public `@channel_name`.
4. Put the bot token in `SANCTIONS_TELEGRAM_BOT_TOKEN` or the configured environment variable.
5. Run `python3 scripts/configure.py --config config.json --mode channel --destination <destination> --verify`.
6. Review anything accumulated in the outbox. Choose one explicit activation policy: publish selected records, publish all records, or establish a current baseline and publish no history. The default is review.
7. Enable the scheduler only after verification succeeds and the activation policy is confirmed.

Do not commit `config.json`, `.env`, databases, logs, generated documents, or service override files containing identifiers.
