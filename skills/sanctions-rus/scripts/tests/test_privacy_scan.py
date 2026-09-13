import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "privacy_scan.py"


class PrivacyScanTests(unittest.TestCase):
    def test_clean_tree_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "SKILL.md").write_text("portable content\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), directory],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_secret_like_value_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            token = "ghp_" + ("A" * 24)
            Path(directory, "config.txt").write_text(token, encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), directory],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("secret", result.stdout)


if __name__ == "__main__":
    unittest.main()
