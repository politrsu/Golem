import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "render_docx.py"


class RenderDocxTests(unittest.TestCase):
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
