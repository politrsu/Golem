# Compact Russian sanctions list

Use this profile for a requested list by the agreed reference format. A request for a DOCX is fulfilled by the document, not by posting its records as chat text.

## Layout

- A4, margins: top/bottom 20 mm, left 30 mm, right 15 mm.
- Verdana 11 pt, line spacing 1.15, normal paragraph spacing after 8 pt.
- Centered bold main heading containing «Антироссийские санкции» and the actual issuing jurisdiction/measure; preserve the heading precedence in the event contract.
- Centered italic date/count summary when a publication date is available; counts refer only to newly designated records.
- Bold non-empty category headings. Use real Word decimal numbering, starting at 1 for each category; compact list paragraphs have no spacing after and stay together. No tables or bullet lists.
- Individuals: bold name, foreign country if known, then a dash and the verified Russian position or substantive role, with active evidence links. Ownership is a role, not proof of an executive title. Do not invent a management position when only ownership is verified.
- Companies: name and foreign country. Vessels: name and one `IMO` label with the source number. Keep other categories only when present in the verified event.
- Render `legal_effect_ru` separately when supplied; do not fold amendments to existing records into new-designation counts.
- End with an active direct official document link. Clear author and last-modified-by metadata.

## Review and missing information

Reconcile the complete stable-ID set and category counts with the official document/annex before rendering. Confirm countries, IMO numbers, positions/roles, and supporting links. Use authoritative role evidence where available; record any researched fallback and its limits. «Должность не установлена», «нет данных», a blank role, and a bare name do not pass the individual gate. Retain the document in enrichment while the already verified news can be delivered under policy.

The bundled renderer checks that a substantive role and evidence URL are present; this does not prove the claim. Upstream review owns factual verification, document scope, completeness, and currency. The renderer does not browse or send messages.

For recovery of an existing reviewed DOCX, use the source/hash-bound manifest procedure in [architecture.md](architecture.md#document-enrichment-and-recovery). Keep compact-list review separate from full grounds translation.
