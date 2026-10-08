#!/usr/bin/env python3
"""Render a compact list after upstream source and role-evidence review."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

CATEGORY_TITLES = {
    "individuals": "Физические лица",
    "entities": "Юридические лица и организации",
    "vessels": "Суда",
    "aircraft": "Воздушные суда",
    "banks": "Банки и финансовые организации",
    "ports": "Порты",
}
UKRAINIAN = re.compile(r"[іїєґІЇЄҐ]")
UNRESOLVED_ROLE = re.compile(
    r"^(?:должность|роль)(?:\s*[:—–-]?\s*(?:не\s+(?:установлен[ао]?|указан[ао]?|известн[ао]?)|уточняется))?[.!]?\s*$"
    r"|^(?:нет данных|неизвестно|не установлено|не указано|n/?a|unknown|[-—–])\s*[.!]?$", re.I)


def http_url(url):
    parsed = urlsplit(str(url or ""))
    if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Source links require an absolute HTTP(S) URL without credentials")
    return url


def display_text(text):
    if UKRAINIAN.search(str(text)):
        raise ValueError("Ukrainian-specific letters remain in display text; translate into Russian first")
    return str(text)


def document_heading(event):
    """Label an upstream-verified Russia-related event without losing its measure."""
    heading = (event.get("document_title_ru") or event.get("title_ru")
               or f"Санкционный список — {event.get('jurisdiction', '')}".rstrip(" —"))
    if "антироссийск" not in heading.casefold():
        heading = f"Антироссийские санкции – {heading}"
    return heading


def validate_display(event):
    display_text(document_heading(event))
    display_text(event.get("legal_effect_ru", ""))
    display_text(event.get("published_date", ""))
    if event.get("official_url"):
        http_url(event["official_url"])
    for key, items in event.get("categories", {}).items():
        if not items:
            continue
        if key not in CATEGORY_TITLES:
            raise ValueError("Unsupported document category; map it to a reviewed Russian section")
        for item in items:
            name = str(item.get("name_ru") or item.get("name") or "").strip()
            if not name:
                raise ValueError("Each record requires a reviewed name")
            for field in ("name_ru", "name", "position_ru", "country_ru"):
                # Original evidence fields stay untouched; only the chosen name is displayed.
                if field == "name" and item.get("name_ru"):
                    continue
                display_text(item.get(field, ""))
            if item.get("imo") and not re.fullmatch(r"(?:IMO\s*)*\d{7}", str(item["imo"]), re.I):
                raise ValueError("Vessel IMO must contain seven digits")
            if key == "individuals":
                role = str(item.get("position_ru") or "").strip()
                if not role or UNRESOLVED_ROLE.fullmatch(role) or not re.search(r"[А-Яа-яЁё]", role):
                    raise ValueError("Individual requires a verified Russian position or substantive role")
                evidence = item.get("position_evidence")
                if not isinstance(evidence, list) or not evidence:
                    raise ValueError("Individual requires position_evidence with source_url")
                for source in evidence:
                    if not isinstance(source, dict):
                        raise ValueError("Role evidence must contain source_url")
                    http_url(source.get("source_url"))


def add_link(paragraph, label, url):
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True))
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    for tag, value in (("color", "0563C1"), ("u", "single")):
        element = OxmlElement("w:" + tag)
        element.set(qn("w:val"), value)
        props.append(element)
    run.append(props)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def new_numbering(document):
    root = document.part.numbering_part.element
    aid = max((int(e.get(qn("w:abstractNumId"))) for e in root.findall(qn("w:abstractNum"))), default=-1) + 1
    nid = max((int(e.get(qn("w:numId"))) for e in root.findall(qn("w:num"))), default=0) + 1
    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), str(aid))
    level = OxmlElement("w:lvl")
    level.set(qn("w:ilvl"), "0")
    for tag, value in (("start", "1"), ("numFmt", "decimal"), ("lvlText", "%1."), ("lvlJc", "left")):
        element = OxmlElement("w:" + tag)
        element.set(qn("w:val"), value)
        level.append(element)
    paragraph_props = OxmlElement("w:pPr")
    indent = OxmlElement("w:ind")
    indent.set(qn("w:left"), "360")
    indent.set(qn("w:hanging"), "360")
    paragraph_props.append(indent)
    level.append(paragraph_props)
    abstract.append(level)
    root.append(abstract)
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(nid))
    ref = OxmlElement("w:abstractNumId")
    ref.set(qn("w:val"), str(aid))
    num.append(ref)
    root.append(num)
    return nid


def render(event, output):
    validate_display(event)
    document = Document()
    document.core_properties.author = ""
    document.core_properties.last_modified_by = ""
    section = document.sections[0]
    for field, value in (("page_width", 210), ("page_height", 297), ("top_margin", 20),
                         ("bottom_margin", 20), ("left_margin", 30), ("right_margin", 15)):
        setattr(section, field, Mm(value))
    normal = document.styles["Normal"]
    normal.font.name = "Verdana"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(8)
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run(document_heading(event)).bold = True
    if event.get("published_date"):
        count = sum(len(items) for items in event.get("categories", {}).values())
        summary = document.add_paragraph()
        summary.alignment = WD_ALIGN_PARAGRAPH.CENTER
        summary.add_run(f"{event['published_date']}. Новых позиций: {count}.").italic = True
    if event.get("legal_effect_ru"):
        document.add_paragraph(event["legal_effect_ru"])
    for key, heading in CATEGORY_TITLES.items():
        items = event.get("categories", {}).get(key, [])
        if not items:
            continue
        paragraph = document.add_paragraph()
        paragraph.add_run(heading).bold = True
        paragraph.paragraph_format.keep_with_next = True
        number = new_numbering(document)
        for item in items:
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.keep_together = True
            numbering = paragraph._p.get_or_add_pPr().get_or_add_numPr()
            numbering.get_or_add_ilvl().val = 0
            numbering.get_or_add_numId().val = number
            paragraph.add_run(item.get("name_ru") or item["name"]).bold = key == "individuals"
            if item.get("country_ru") and item["country_ru"] != "Россия":
                paragraph.add_run(f" ({item['country_ru']})")
            if key == "individuals":
                paragraph.add_run(" – " + item["position_ru"])
                for source in item["position_evidence"]:
                    add_link(paragraph, " [источник]", source["source_url"])
            if item.get("imo"):
                imo = re.sub(r"^(?:IMO\s*)+", "", str(item["imo"]), flags=re.I)
                paragraph.add_run(f" (IMO {imo})")
    if event.get("official_url"):
        paragraph = document.add_paragraph("Оригинал документа: ")
        add_link(paragraph, event["official_url"], event["official_url"])
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: render_docx.py EVENT.json OUTPUT.docx")
    event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    try:
        render(event, sys.argv[2])
    except ValueError as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
