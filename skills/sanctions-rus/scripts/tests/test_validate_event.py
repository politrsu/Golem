import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_event.py"
SPEC = importlib.util.spec_from_file_location("validate_event", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ValidateEventTests(unittest.TestCase):
    def test_rejects_google_news_wrapper(self):
        errors = validator.validate_event({
            "structured": True,
            "authority_domain": "ofac.treasury.gov",
            "official_url": "https://news.google.com/rss/articles/example?oc=5",
        })
        self.assertIn("official_url must not use a search/news wrapper", errors)
        self.assertIn("official_url host must belong to authority_domain", errors)

    def test_accepts_direct_authority_document(self):
        errors = validator.validate_event({
            "structured": True,
            "authority_domain": "treasury.gov",
            "official_url": "https://ofac.treasury.gov/recent-actions/20300102",
        })
        self.assertEqual(errors, [])

    def test_rejects_authority_homepage(self):
        errors = validator.validate_event({
            "structured": True,
            "authority_domain": "treasury.gov",
            "official_url": "https://home.treasury.gov/",
        })
        self.assertIn("official_url must identify a document or detail page", errors)


if __name__ == "__main__":
    unittest.main()
