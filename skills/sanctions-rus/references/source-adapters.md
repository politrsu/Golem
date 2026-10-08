# Source adapter acceptance

Use this reference when implementing or repairing official-source adapters. These are reusable parsing and acceptance requirements, not bundled adapters or a claim of live coverage. Keep current official URLs in deployment configuration. Use complete documents and synthetic or sanitized public fixtures; never publish private snapshots, receipts, or runtime state.

## United States

Preserve complete OFAC action boundaries across wrapped HTML anchors. Fetch action detail and all relevant linked documents before filtering a mixed-programme action for Russia relevance. Resolve ambiguous identities against the full official SDN data using stable IDs; metadata-only identity-proof refreshes must not generate a second event or DOCX. Streaming the large identity list can bound memory use. Preserve additions, `old -to- new` variations, removals, programme changes, and secondary-sanctions status as distinct operations.

Treasury press coverage needs complete article bodies and matching document identity. A financial-literacy or another-country article can be explicitly outside monitored scope only with full-body evidence and a supported decision rule. A non-Russia card title alone never justifies dropping a mixed action. Test wrapped anchors, mixed regimes, missing/ambiguous identities, incomplete bodies, and changing proof metadata.

## European Union

Read the full operative text and annexes, match the act identity and legal basis, and distinguish sanctions measures from financial-support decisions such as Ukraine Facility payments. An outside-scope decision needs the complete document, hash, and reason; unknown wording or mixed measures stays reviewable. Keep commencement and application dates distinct. Preserve existing additions, amendments, removals, and legal-act routes; test positive sanctions cases as well as complete, truncated, and mixed outside-scope candidates.

## United Kingdom

Resolve canonical Atom/list aliases only after successful parsing of the complete official Russia-regime CSV/XML snapshot. Compare stable `Unique ID` records; an alias is not permission to consume an arbitrary discovery URL. A failed snapshot leaves both the discovery and semantic checkpoint unresolved. Test legitimate aliases, unrelated URLs, failed/truncated snapshots, and record-level additions, variations, and removals.

An official press article may corroborate an already verified package without creating another news event or DOCX. Review the complete article against the specific notice, stable-ID delta, publication date, category counts, and named records; require a fresh complete list comparison showing no additional delta. Retain the article URL/hash and its binding to the verified event. Reconcile any existing delivery from its bound receipt without sending again. Do not generalize a one-off reviewed match into a title/keyword suppression rule: extra measures, inconsistent counts, a missing article body, or an unresolved list comparison keep the discovery pending. This review proves neither a new delivery nor a new legal change.

## Switzerland

Read the complete SECO article and verify its identity before classifying a reconstruction-funding announcement outside sanctions. Retain the document hash and concrete reason; keywords alone are insufficient. Preserve structured list and Fedlex legal-act routes. Test complete outside-scope articles, incomplete bodies, mixed restrictive measures, and existing sanctions changes.

For the full SECO XML download, negotiate HTTP compression when supported while preserving the 15-second request limit and at most one retry per unavailable source. A timeout, partial body, invalid XML, or incomplete sanctions scope retains the last verified snapshot and leaves current semantic coverage incomplete. An earlier successful download does not cover a later failed cycle. Attempt the source again in the next full 10-minute slot; disabled operational messages do not make health successful. Compression is a transport aid, not evidence that source instability is fixed.

## Japan

Parse all referenced annexes and the complete gazette/legal/FAQ context, including short PDFs with vertical text. Keep financial designations, export-restricted entities, vessel-services restrictions, and announced goods measures separate. Use source-specific stable IDs, verify counts against annex contents, and deduplicate vessel IMO numbers only after validating their checksums. Preserve original names, roles, addresses, annex lineage, publication dates, commencement, transitions, and exceptions.

Do not invent commodity codes or effective dates absent from an announcement. Mark those limitations explicitly and retain any unresolved implementing document for review. Do not render export or vessel-services restrictions as asset freezes. A changed grammar, missing annex, incomplete FAQ/legal context, invalid IMO, ambiguous ID, or count mismatch blocks semantic completion. Tests must cover those failures as well as complete multi-annex notices, vertical PDF extraction, and each distinct measure type. Keep one list-delivery owner to prevent financial and export lists from being conflated or replayed.

The MOF financial-list CSV can appear with the next UTC day's filename before that day begins. A narrow unchanged-content check may confirm no change only when a prior verified snapshot exists, the parser version matches, the completely parsed non-empty record set equals that snapshot in every field, non-empty scope counts match, the observation is later than the baseline check, and the filename is exactly one day ahead. Record this as an unchanged observation with `future_version_accepted=false`; keep the verified snapshot and its version intact and create no event. Equality of counts or material fingerprints alone is insufficient. Any record or metadata difference, incomplete scope, first baseline, parser mismatch, reversed observation time, or more distant date remains blocked. Test both the unchanged case and these rejection boundaries; this exception does not authorize future-dated designations or apply to other sources.

## Regression and collection boundaries

Keep existing Australia and Canada adapters and required-source coverage in regression checks when changing shared parsing. Bound each network request and collector run; retry a transient transport failure only within the configured finite budget. Unknown legal grammar is a semantic failure, not a reason for repeated blind fetching. A notification-free shadow cycle must establish semantic coverage for every configured jurisdiction before checkpoint migration; fetch success alone is insufficient. Do not publish a historical backlog as a test.
