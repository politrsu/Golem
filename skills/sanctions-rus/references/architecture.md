# Architecture

## Separation of concerns

Keep two independent lanes:

1. **Sensor lane:** scheduler → official-source adapters → discovery store → source-specific parser → snapshot diff → publication gate → deduplicator → transactional alert outbox → Telegram. This lane is deterministic and must not require an LLM.
2. **Enrichment lane:** verified new-designation event → translation/research worker → DOCX renderer → document outbox → Telegram. This lane may use a model. Failure here never blocks the sensor lane.

These are integration requirements; the reusable package does not ship a running collector, outbox implementation, admission controller, or source adapters. Preserve the deployment's explicit publication policy. In documents-only mode, omit text delivery without treating it as a failed prerequisite for document preparation.

## Event states

`discovered → pending_enrichment → verified → alert_pending → alert_sent → enrichment_pending → enriched → document_pending → complete`

A parse failure remains in `pending_enrichment`; it does not become a user alert. Keep separate durable markers for source change detected, structured event verified, alert delivered, and document delivered. Use separate idempotency keys and delivery acknowledgements for the alert and document. Store the source URL, content hash, first-seen time, effective date, stable authority IDs, snapshot version, and parser version.

The diagram describes the alert-and-document path. An authorized documents-only path proceeds from `verified` to `enrichment_pending` without inventing `alert_sent`. An unresolved send enters `review_required`; it does not loop automatically back to sending. Policy holds and uncertain delivery evidence survive restarts, translation changes, and queue reconciliation.

## Publication gate

Default deny. Generic page changes and unknown event types have `alertable=false`. Publication requires a source-specific structured event:

- designations: stable IDs and verified non-empty category counts;
- variation: stable ID, record name, and material changed fields;
- delisting/revocation: stable ID, record name, and category;
- legal change/licence: official act identifier and direct official URL.

If authoritative structured data is unavailable or malformed, retain the discovery for retry and record an internal health failure; send an operational notification only if that independent route is enabled. Never advance the verified snapshot on a failed or partial parse.

## Snapshot rules

Build the first snapshot as a silent baseline. Compare later snapshots by stable authority ID. Separate material fields from volatile metadata such as download timestamps or formatting. Commit a new snapshot atomically only after complete parsing. Preserve the previous snapshot until the diff and pending events are durably recorded.

## Source health

- Assign at least one required direct official source to every jurisdiction.
- A search or news feed is discovery-only and cannot make source health green.
- On a required-source failure, do not advance that jurisdiction's checkpoint.
- Bound each external request to 15 seconds with at most one retry per unavailable source. Backoff may limit retries inside a cycle, but must not suppress a required source in the next scheduled full cycle. Record health independently of whether operational notifications are enabled.
- Normalize redirect and tracking URLs to the canonical official URL before deduplication.

Report three distinct measurements:

- **Fetch coverage:** required endpoints returned usable responses.
- **Semantic coverage:** every required source was fully parsed, diffed, or explicitly classified outside monitored scope with full-document identity, hash, and reason. Unknown grammar, missing annexes, partial bodies, or unresolved stable IDs keep this incomplete.
- **Delivery-inclusive health:** semantic coverage plus the state of authorized deliveries, pending enrichment, and review holds. Semantic success does not erase a delivery hold or prove a new send.

Maintain a separate semantic checkpoint per jurisdiction and advance it only after all required processing succeeds. Preserve older checkpoints and run history when adding this measurement. Record policy-suppressed text separately from unparsed discoveries. A quiet cycle or an old delivery receipt is insufficient evidence of current end-to-end delivery.

### Full-cycle cadence and notification policy

The standard profile covers US, EU, UK, CH, CA, AU, and JP every 10 minutes. Use calendar slots (for example 12:00, 12:10, 12:20), not elapsed time since the previous completion: jitter must not turn a nominal 10-minute timer into a 20- or 30-minute full-source interval. Store full-cycle attempts separately from successful semantic checkpoints. A failed source is attempted again in the next full slot; optional targeted retries never count as a full cycle. Serialize overlapping collectors and report missed/delayed slots rather than claiming coverage.

Store three independent booleans: `notify_alerts` for sanctions news, `notify_operational` for service/health messages, and `notify_documents` for DOCX. The standard news-plus-document profile is true/false/true with `require_alert_before_docx=true`. It is a deployment profile, not permission to overwrite an existing user policy. Internal error records and incomplete coverage remain visible in state when service messages are disabled.

When both outputs are required, match the news acknowledgement to the same event and destination before document delivery. A manually delivered private-chat document or an old news receipt for another event cannot satisfy channel acceptance. In an explicitly authorized documents-only mode, record policy suppression without inventing a news receipt.

### Official fallback migration

If an official API is removed, blocked, or persistently unavailable, use another public endpoint owned by the same authority. A server-rendered official page or official downloadable document may replace the API only when it exposes enough information to preserve document identity, version, publication dates, and coverage checks.

For pages that embed server-side application state, extract the exact JSON script payload and parse it before decoding individual text fields. Do not HTML-decode the complete JSON payload: encoded quotation marks inside string values can become bare quotes and corrupt otherwise valid JSON.

Treat a fallback as a parser change. Add fixtures for valid and malformed payloads, run a full notification-free shadow cycle, and verify every required source and jurisdiction before advancing the affected checkpoint. Keep fail-closed behavior unchanged.

### Collection during model load

Where the deployment supports it, give only the fixed deterministic collector command a separately admitted, bounded resource lane with document/model work deferred. Verify command identity and service/cgroup ownership, serialize collectors, and enforce finite admission and execution deadlines. Account for the collector's remaining allocation plus reserve against host availability and every constrained ancestor; check pressure both before and during execution. Reduce parser concurrency or stream large lists when needed.

Keep existing CPU, memory, swap, and shared limits. Stop only the collector process group owned by that run. Never release another task's lease, reclassify arbitrary heavy work as control work, cancel its owner, or bypass approval to gain capacity. If admission cannot be established safely, report delayed/degraded collection. Test pressure rejection, ownership mismatch, deadline expiry, and collection under an active model owner. Short observations do not establish a long-term SLA; no deployment-specific unit names or capacity values are prescribed here.

## Storage

Prefer SQLite in WAL mode for a single-host deployment. Keep configuration, secrets, runtime state, snapshots, and generated files outside the skill directory. Back up the database and test restore procedures.

## Telegram delivery

Supported modes:

- `channel`: validate the destination and the bot's posting rights before enabling delivery.
- `agent_chat`: deliver alerts and DOCX files to the user's current primary agent conversation when no dedicated channel exists.
- The transactional outbox is a failure buffer, not the default user-facing destination.

Choose the destination explicitly during onboarding and confirm it with a test message. Never copy a private chat or channel identifier into the reusable skill or repository.

Test messages require explicit authorization. Preserve one delivery owner for each artifact and completion notification. Recovery does not authorize replay of historical records or activation of a paused route; respect cutoff and backlog policy even when parsing has recovered.

### Delivery intent and recovery

Before a sender call, durably persist an intent with an attempt ID, semantic delivery identity, complete event hash, destination digest, and immutable artifact SHA-256. Serialize transactions for the canonical outbox. If using file journals, atomically replace and fsync both files and their containing directory; intent must survive main-state failure. Keep evidence outside the reusable package.

Persist a validated positive platform receipt before removing the queued job. The sender adapter must associate the platform message ID and acknowledged destination with the exact artifact and attempt; a bare boolean or locally invented message ID is insufficient. On restart, validate all bindings and reconcile a durable receipt without calling the sender again. Remove acknowledged entries from the current canonical queue; persistence or deduplication may replace the list, making an earlier in-memory reference stale. Test recovery with real persistence as well as a fake sender.

| Observed outcome | Recovery |
| --- | --- |
| Matching durable positive receipt; queue update failed | Record delivery and reconcile queue without resending. |
| Explicit negative platform acknowledgement or established non-attempt | A bounded automatic retry may reuse the bound artifact under the same publication policy. |
| Timeout, exception, lost acknowledgement, bare boolean, or crash with only intent persisted | Retain `review_required`; do not automatically resend. |
| Missing/corrupt journal or event, destination, or artifact binding mismatch | Retain evidence and require authoritative reconciliation; do not regenerate and retry. |
| Recovered historical event without publication permission | Retain policy hold with no send attempt. |

Deduplicate by semantic content, excluding changing retrieval/identity-proof metadata. Retain a complete payload hash separately for binding. Archive reconciliation evidence for duplicate pending jobs and acknowledged identities; keep the job containing unresolved send evidence and do not let enrichment overwrite it. Preserve receipts and intent journals during rollback or restore. Reconcile uncertain sends from authoritative evidence; absence of a receipt does not prove absence of a send. This reduces duplicate risk but does not promise exactly-once delivery from Telegram.

Use an offline fake sender to test durable intent before invocation, both crash windows around acknowledgement persistence, restarts, corrupt bindings, definite rejection, metadata variants, duplicate pending jobs, and historical holds. Live acceptance requires a genuine authorized event and a bound receipt; passing these local tests or reporting healthy sources is not live delivery proof.

## Document enrichment and recovery

Keep translation admission failure, model/CLI exit failure, invalid translation, and send failure as distinct durable outcomes. Save bounded, redacted diagnostics and leave the verified event queued. Model errors must not block deterministic collection or erase already acknowledged news.

A non-zero CLI exit does not prove that a generated sidecar is invalid, and a zero exit does not prove validity. Reuse a sidecar only after the normal source-identity, complete-record, Russian-content, role-evidence, and document gates pass. Do not set verification flags merely because a file exists.

An already reviewed compact DOCX may be recovered without repeating full translation if a manifest binds its exact SHA-256, source/document identity, complete stable-ID set, categories, displayed names, countries, roles with evidence, and vessel IMO numbers. Validate its numbered paragraphs and active original/evidence links before reuse. Label this `reviewed_reference_compact`; it is not evidence that the full grounds for designation were translated. A changed source or artifact invalidates the binding. The deployment implements this recovery; the bundled renderer only builds new compact lists.
