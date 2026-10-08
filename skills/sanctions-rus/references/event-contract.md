# Normalized event contract

All publishable events require `structured: true`, a stable `event_id`, jurisdiction, dates, `authority_domain`, a direct `official_url` on that domain, and source parser version. Discovery URLs belong in internal state only. Search/news wrappers and redirectors must never populate `official_url`.

The upstream adapter must establish Russia-related scope from the complete official document and regime, including applicable measures on third-country entities. The renderer does not infer relevance from nationality or verify the legal scope. Keep unrelated sanctions outside this workflow.

## New designations

```json
{
  "event_id": "authority:document-or-version:designations",
  "structured": true,
  "jurisdiction": "Example jurisdiction",
  "event_type": "designations",
  "published_date": "2030-01-02",
  "effective_date": "2030-01-01",
  "title_ru": "Новые санкционные ограничения",
  "authority_domain": "authority.example",
  "official_url": "https://authority.example/original-act",
  "parser_version": "2",
  "categories": {
    "individuals": [{"authority_id": "P-1", "name_ru": "Иван Иванов", "position_ru": "Директор ООО «Пример»", "position_evidence": [{"source_url": "https://authority.example/original-act"}]}],
    "vessels": [{"authority_id": "V-1", "name_ru": "Пример", "imo": "1234567"}]
  }
}
```

Omit absent categories or use empty arrays internally. Alerts and DOCX output display only categories containing records.

For the DOCX main heading, optional `document_title_ru` takes precedence over `title_ru`. Preserve the issuing jurisdiction and actual measure, for example `Япония: новые организации под экспортными ограничениями`. The renderer adds `Антироссийские санкции – ` unless the selected heading already contains `антироссийск` case-insensitively; existing wording is retained. If both title fields are empty, it uses `Санкционный список — <jurisdiction>`. Provide a verified measure-specific title whenever available; do not infer asset freezes from export or vessel-services restrictions.

Keep semantic delivery identity separate from the complete event hash: identity includes official document, jurisdiction/regime, event type, actual measure, stable record IDs and material changes; the event hash binds the exact reviewed payload. Retrieval timestamps or refreshed identity-proof metadata alone must not create a second deliverable. Preserve that evidence separately, along with original text, annex provenance, parser version, and publication/effective dates.

## Variation

```json
{
  "event_id": "authority:record-id:snapshot-version",
  "structured": true,
  "jurisdiction": "Example jurisdiction",
  "event_type": "variation",
  "published_date": "2030-01-02",
  "authority_domain": "authority.example",
  "official_url": "https://authority.example/change-notice",
  "parser_version": "2",
  "records": [{
    "authority_id": "R-1",
    "name": "Example entity",
    "category": "entity",
    "changed_fields": ["address", "statement_of_reasons"]
  }]
}
```

A delisting/revocation uses the same record identity fields with `event_type: "delisting"`. A generic source-change event may exist internally but must never carry `structured: true` and must never enter the user alert outbox. Russian display fields must contain reviewed Russian text; translate Ukrainian text before rendering and preserve original evidence separately.

## Compact document fields

Follow [document-format.md](document-format.md). `position_ru` is required for each individual and must give a verified position or substantive role, not a placeholder. Supply a non-empty `position_evidence` array with `source_url` per source; the renderer validates URL structure and embeds these links, while upstream review must verify that the evidence supports the role. Use `country_ru` for foreign records and `imo` for vessels when present in the source. `legal_effect_ru` may describe separate restrictions without counting existing records as new designations. Preserve full original/translated grounds internally; the compact DOCX is not a full-text translation.

The renderer checks displayed Russian text, not raw original-language evidence. Preserve original names, citations, and source URLs intact. Translate Ukrainian content into Russian; mechanical letter substitution is not translation. Do not invent missing names, roles, countries, or IMO numbers.
