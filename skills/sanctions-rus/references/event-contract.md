# Normalized event contract

All publishable events require `structured: true`, a stable `event_id`, jurisdiction, dates, `authority_domain`, a direct `official_url` on that domain, and source parser version. Discovery URLs belong in internal state only. Search/news wrappers and redirectors must never populate `official_url`.

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
    "individuals": [{"authority_id": "P-1", "name_ru": "Иван Иванов", "position_ru": "должность"}],
    "vessels": [{"authority_id": "V-1", "name_ru": "Пример", "imo": "1234567"}]
  }
}
```

Omit absent categories or use empty arrays internally. Alerts and DOCX output display only categories containing records.

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

A delisting/revocation uses the same record identity fields with `event_type: "delisting"`. A generic source-change event may exist internally but must never carry `structured: true` and must never enter the user alert outbox. Russian fields must contain Russian text; normalize Ukrainian-specific letters before rendering.
