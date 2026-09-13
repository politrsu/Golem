# Architecture

## Separation of concerns

Keep two independent lanes:

1. **Sensor lane:** scheduler → official-source adapters → discovery store → source-specific parser → snapshot diff → publication gate → deduplicator → transactional alert outbox → Telegram. This lane is deterministic and must not require an LLM.
2. **Enrichment lane:** verified new-designation event → translation/research worker → DOCX renderer → document outbox → Telegram. This lane may use a model. Failure here never blocks the sensor lane.

## Event states

`discovered → pending_enrichment → verified → alert_pending → alert_sent → enrichment_pending → enriched → document_pending → complete`

A parse failure remains in `pending_enrichment`; it does not become a user alert. Keep separate durable markers for source change detected, structured event verified, alert delivered, and document delivered. Use separate idempotency keys and delivery acknowledgements for the alert and document. Store the source URL, content hash, first-seen time, effective date, stable authority IDs, snapshot version, and parser version.

## Publication gate

Default deny. Generic page changes and unknown event types have `alertable=false`. Publication requires a source-specific structured event:

- designations: stable IDs and verified non-empty category counts;
- variation: stable ID, record name, and material changed fields;
- delisting/revocation: stable ID, record name, and category;
- legal change/licence: official act identifier and direct official URL.

If authoritative structured data is unavailable or malformed, retain the discovery for retry and emit only an operational health notification. Never advance the verified snapshot on a failed or partial parse.

## Snapshot rules

Build the first snapshot as a silent baseline. Compare later snapshots by stable authority ID. Separate material fields from volatile metadata such as download timestamps or formatting. Commit a new snapshot atomically only after complete parsing. Preserve the previous snapshot until the diff and pending events are durably recorded.

## Source health

- Assign at least one required direct official source to every jurisdiction.
- A search or news feed is discovery-only and cannot make source health green.
- On a required-source failure, do not advance that jurisdiction's checkpoint.
- Use bounded timeouts, exponential backoff, circuit breaking, and an independent health notification.
- Normalize redirect and tracking URLs to the canonical official URL before deduplication.

## Storage

Prefer SQLite in WAL mode for a single-host deployment. Keep configuration, secrets, runtime state, snapshots, and generated files outside the skill directory. Back up the database and test restore procedures.

## Telegram delivery

Supported modes:

- `channel`: validate the destination and the bot's posting rights before enabling delivery.
- `agent_chat`: deliver alerts and DOCX files to the user's current primary agent conversation when no dedicated channel exists.
- The transactional outbox is a failure buffer, not the default user-facing destination.

Choose the destination explicitly during onboarding and confirm it with a test message. Never copy a private chat or channel identifier into the reusable skill or repository.
