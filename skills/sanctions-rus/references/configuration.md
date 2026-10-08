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
  "monitoring": {
    "jurisdictions": ["US", "EU", "UK", "CH", "CA", "AU", "JP"],
    "full_cycle_minutes": 10
  },
  "notifications": {
    "notify_alerts": true,
    "notify_operational": false,
    "notify_documents": true,
    "require_alert_before_docx": true
  },
  "database": "./runtime/sanctions.sqlite3",
  "output_directory": "./runtime/documents"
}
```

## New user without a dedicated channel

1. Installation leaves the scheduler disabled.
2. Select `agent_chat`. In an agent platform, bind it to the current primary conversation. In standalone Telegram mode, provide that private chat's numeric identifier.
3. Obtain explicit authorization for the onboarding test, send it, and verify delivery.
4. Enable the scheduler. New alerts and their DOCX files now arrive in the main agent chat.

## User with a dedicated channel

1. Create the Telegram channel manually.
2. Add the bot as an administrator and allow it to post messages.
3. Obtain the numeric channel identifier or use a public `@channel_name`.
4. Put the bot token in `SANCTIONS_TELEGRAM_BOT_TOKEN` or the configured environment variable.
5. With explicit authorization for the test send, run `python3 scripts/configure.py --config config.json --mode channel --destination <destination> --verify`.
6. Review anything accumulated in the outbox. Choose one explicit activation policy: publish selected records, publish all records, or establish a current baseline and publish no history. The default is review.
7. Enable the scheduler only after verification succeeds and the activation policy is confirmed.

Do not commit `config.json`, `.env`, databases, logs, generated documents, or service override files containing identifiers.

An update preserves the existing destination, publication mode (including documents-only), pauses, cutoff, historical-record policy, and delivery owner. It does not run onboarding again or authorize a test message. Unknown send outcomes require receipt reconciliation independently of any backlog publication permission. Keep unresolved intent and receipt journals when upgrading or restoring state.

## Scheduling and independent notifications

`configure.py` creates onboarding delivery configuration only; the monitoring and notification objects above are integration requirements for the deployment, not a bundled scheduler. Map them explicitly to the collector, news sender, operational notifier, and document worker. A single global text switch or the mere existence of a pause file must not silently suppress both service messages and sanctions news.

Use all seven jurisdictions every 10 minutes for the standard profile. Verify attempts per required source across consecutive slots, not merely timer activation. Respect explicit alternative scope/cadence. Source outages keep semantic coverage incomplete even though the scheduled attempt happened.

For news followed by DOCX, enable news/documents and require the matching news receipt; operational notifications may remain off. For an explicit documents-only request, disable news and the news prerequisite, keep documents enabled, and preserve internal health records. Apply the user's latest explicit policy when migrating older settings; a request to stop service alerts alone does not authorize disabling sanctions news. Keep held historical records and uncertain send outcomes under their existing review policy.
