import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render_docx.py"


class RenderDocxTests(unittest.TestCase):
    def render(self, event):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "event.json"
            output = Path(directory) / "result.docx"
            source.write_text(json.dumps(event, ensure_ascii=False), encoding="utf-8")
            subprocess.run(["python3", str(SCRIPT), str(source), str(output)], check=True)
            return Document(output)

    def test_russia_related_third_country_export_list_preserves_measure_and_records(self):
        event = {
            "jurisdiction": "Япония",
            "document_title_ru": "Япония: новые организации под экспортными ограничениями",
            "title_ru": "Общее название сообщения",
            "official_url": "https://authority.example/export-notice",
            "categories": {"entities": [
                {"name_ru": f"Пример организации {index}", "country_ru": "Третья страна"}
                for index in range(1, 5)
            ]},
        }
        document = self.render(event)
        self.assertEqual(document.paragraphs[0].text,
                         "Антироссийские санкции – " + event["document_title_ru"])
        text = "\n".join(p.text for p in document.paragraphs)
        for item in event["categories"]["entities"]:
            self.assertIn(item["name_ru"] + " — " + item["country_ru"], text)
        self.assertIn(event["official_url"], text)
        self.assertNotIn("замораживание", text.casefold())

    def test_existing_heading_is_preserved_without_duplicate_prefix(self):
        for heading in (
            "Антироссийские санкции – Япония: экспортные ограничения",
            "Япония: АНТИРОССИЙСКИЕ САНКЦИИ — экспортные ограничения",
        ):
            with self.subTest(heading=heading):
                document = self.render({"title_ru": heading, "categories": {}})
                self.assertEqual(document.paragraphs[0].text, heading)
                self.assertEqual(document.paragraphs[0].text.casefold().count("антироссийск"), 1)

    def test_generated_heading_can_be_reused_without_another_prefix(self):
        event = {"title_ru": "Япония: экспортные ограничения", "categories": {}}
        first = self.render(event).paragraphs[0].text
        event["document_title_ru"] = first
        self.assertEqual(self.render(event).paragraphs[0].text, first)

    def test_empty_document_title_uses_title_then_jurisdiction_fallback(self):
        cases = [
            ({"document_title_ru": "", "title_ru": "Канада: новые включения", "jurisdiction": "Канада"},
             "Антироссийские санкции – Канада: новые включения"),
            ({"document_title_ru": None, "title_ru": "", "jurisdiction": "Япония"},
             "Антироссийские санкции – Санкционный список — Япония"),
            ({}, "Антироссийские санкции – Санкционный список"),
        ]
        for event, expected in cases:
            with self.subTest(event=event):
                self.assertEqual(self.render(event).paragraphs[0].text, expected)

    def test_renders_only_non_empty_categories_and_clears_author(self):
        event = {
            "title_ru": "Новые санкционные ограничения",
            "official_url": "https://authority.example/original-act",
            "categories": {
                "individuals": [{"name_ru": "Иван Иванов", "position_ru": "должность"}],
                "vessels": [],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "event.json"
            output = Path(directory) / "result.docx"
            source.write_text(json.dumps(event, ensure_ascii=False), encoding="utf-8")
            subprocess.run(["python3", str(SCRIPT), str(source), str(output)], check=True)
            document = Document(output)
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            self.assertIn("Физические лица", text)
            self.assertNotIn("Суда", text)
            self.assertEqual(document.core_properties.author, "")

    def test_rejects_untranslated_ukrainian_letters(self):
        event = {"title_ru": "Перелік", "categories": {}}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "event.json"
            output = Path(directory) / "result.docx"
            source.write_text(json.dumps(event, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), str(source), str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
