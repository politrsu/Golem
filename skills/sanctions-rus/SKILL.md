---
name: "sanctions-rus"
description: "Monitors official sanctions sources, verifies record-level changes, sends fail-closed alerts, and builds Russian DOCX reports."
---

# Sanctions RUS

Use this skill to configure, audit, or run a sanctions-monitoring workflow. Keep urgent detection deterministic. Run translation and document preparation only after a verified, structured event exists.

## Operating contract

1. Poll configured official sources on schedule. Require at least one direct official source per jurisdiction; never let search results mask its failure.
2. Extract publication/effective dates, title, jurisdiction, canonical original URL, document version, content fingerprint, and parser version.
3. Treat a changed landing page, list timestamp, ETag, or generic notice as a discovery signal only. It is never publishable by itself.
4. After discovery, fetch the authoritative structured list or act and compare it with the last verified snapshot by the authority's stable record identifier.
5. Classify record-level changes:
   - identifier appears: new designation;
   - existing identifier changes materially: variation/amendment;
   - identifier disappears: revocation/delisting;
   - only timestamps, formatting, aliases, or other non-material technical fields change: correction.
6. Open the original act and every relevant annex. Count only newly added positions by categories actually present: individuals, entities, vessels, aircraft, banks, ports, or other explicit categories. Do not count aliases or corrected attributes as new positions.
7. Publish only fully structured events. A new-designation alert must contain verified non-zero category counts. A variation or removal alert must identify the affected record, stable ID, and material change. Never render internal event names such as `list_or_notice_update`.
8. If parsing, download, comparison, or verification fails, keep the discovery in `pending_enrichment`, send an operational health signal, and publish no user alert. Retry idempotently without advancing the verified snapshot.
9. If the count cannot be verified, say so only in the internal review queue; never invent a number or send a generic list-update alert.
10. Publish the urgent alert first. Include jurisdiction, event type, date, only non-zero category counts or concrete changed records, and the direct official document URL.
11. Mark the alert delivered only after Telegram acknowledges it. Retain failed deliveries in the outbox and retry idempotently.
12. Translate the complete new list into Russian after a new-designation alert. Translate Ukrainian-language text into Russian as well.
13. Build a DOCX only for new records, using only non-empty sections. Never print empty headings or phrases such as “не добавлены”. Include positions for individuals and IMO numbers for vessels when available.
14. Deliver the translated DOCX to the same configured Telegram destination. Its failure must not delay or invalidate the urgent alert. Variations, corrections, and removals do not create a “new list” DOCX unless explicitly configured.

## Publication gate

The publisher must default to deny:

- `alertable = false` for unknown, generic, or unparsed events;
- allow publication only for event types validated by a source-specific adapter;
- require `structured = true` and the event-specific fields from the normalized contract;
- keep `detected`, `verified`, and `delivered` as separate durable states;
- update the authoritative snapshot only after a successful full parse;
- never mark a discovery consumed merely because a page changed.

For the UK Sanctions List, fetch the official CSV/XML after GOV.UK reports a change. Restrict the snapshot to the relevant sanctions regime and compare records by `Unique ID`. Ignore `Last Updated` by itself. New IDs produce designation events; changed material fields produce variation events; missing IDs produce delisting events. A first installation records a baseline without publishing historical records.

## Telegram onboarding

Read [references/configuration.md](references/configuration.md). A bot cannot create a Telegram channel.

- If a dedicated channel exists, require the user to add the bot as an administrator with permission to post, then validate access before activation.
- If no dedicated channel exists, select `agent_chat` and bind delivery to the user's current primary agent conversation. Send both alerts and DOCX files there.
- Send a test message and require successful delivery before enabling the scheduler.
- Store the bot token only in an environment variable or secret manager. Keep channel identifiers in local configuration, never in the skill or repository.

For a standalone Telegram bot, run `python3 scripts/configure.py --config ./config.json --mode agent_chat --destination ... --verify` and supply the current private-chat identifier. In an agent platform, use its current-conversation binding instead of copying a numeric identifier into the repository. For a channel, use `--mode channel --destination ... --verify`.

If delivery is temporarily unavailable, retain records in the local outbox. Before reconnecting any destination, ask how to handle queued records: review and publish selected records, publish all, or establish a current baseline without publishing history. Default to review; never flood a destination automatically.

## Reliability rules

Follow the state model and failure boundaries in [references/architecture.md](references/architecture.md). Use SQLite or another transactional store for checkpoints, snapshots, pending enrichment, and outboxes. Advance a jurisdiction checkpoint only after its required official source was successfully checked. Return a non-zero service exit code on a critical source or persistence failure and send an independent operational alert.

When an official API becomes unavailable or blocks automated requests, migrate only to another public endpoint controlled by the same authority. Prefer a server-rendered official page or official downloadable document. If the page embeds structured application state, parse that state as JSON without HTML-decoding the complete script body first; decode individual extracted text fields instead. Require the same document identity, version, dates, and coverage checks as for the API. Keep the old checkpoint until a full shadow cycle confirms every required source and jurisdiction.

For cross-programme actions, do not apply the Russia relevance filter to an index-card title alone. If an official action card announces a designation, list update, amendment, or delisting, fetch the authoritative detail page first. Match changed records to Russian entities using the record body and stable identifiers; parse `old -to- new` rows as variations, including newly added sanctions programmes and secondary-sanctions status. If detail enrichment fails, retain the discovery, fail the source coverage check, and do not advance its checkpoint.

Before enabling publication, test at least: new designation, variation, technical correction, delisting, unavailable or malformed structured list, first baseline, failed Telegram delivery, duplicate retry, any fallback parser introduced for an official source, and a cross-programme case whose card title omits Russia while the changed record is Russian. Run one complete shadow cycle with notifications disabled, confirm all required jurisdictions remain covered, then enable the scheduler.

After a material monitoring improvement, prepare a sanitized reusable release. Run the package tests and privacy scan, publish only if both pass, and never include production configuration, runtime state, secrets, destinations, logs, or private paths. Keep repository-specific branch and push permissions outside the reusable skill.

## Input and output

Use the normalized event contract in [references/event-contract.md](references/event-contract.md). Render a document with:

```bash
python3 scripts/render_docx.py event.json sanctions-list.docx
```

Validate the package before sharing:

```bash
python3 -c 'import docx'
python3 scripts/privacy_scan.py .
python3 -m unittest discover -s scripts/tests -v
```

Do not include production tokens, chat identifiers, local absolute paths, state databases, logs, real user names, employer names, or document author metadata in a reusable package.
