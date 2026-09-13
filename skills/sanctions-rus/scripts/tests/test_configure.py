import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "configure.py"
SPEC = importlib.util.spec_from_file_location("configure", SCRIPT)
CONFIGURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONFIGURE)


class ConfigureTests(unittest.TestCase):
    def test_transport_failure_does_not_expose_token(self):
        token = "bot-token-that-must-stay-private"
        with patch.object(CONFIGURE.urllib.request, "urlopen", side_effect=OSError(token)):
            with self.assertRaisesRegex(RuntimeError, "Telegram API request failed: getMe") as error:
                CONFIGURE.api(token, "getMe", {})
        self.assertNotIn(token, str(error.exception))


if __name__ == "__main__":
    unittest.main()
