import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.core import translator


class TranslateJsonFileTests(unittest.TestCase):
    @patch("src.core.translator.GoogleTranslator")
    @patch("src.core.translator.translate_text")
    def test_translate_json_file_translates_nested_dicts(
        self, mock_translate_text, mock_translator
    ) -> None:
        mock_translator.return_value = object()
        mock_translate_text.side_effect = (
            lambda _translator, text: f"ja:{text}"
        )

        payload = {
            "title": "Hello",
            "details": {"subtitle": "World", "nested": {"deep": "Value"}},
            "count": 3,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "en_us.json")
            with open(source_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False)

            self.assertTrue(translator.translate_json_file(source_path))

            target_path = os.path.join(temp_dir, "ja_jp.json")
            with open(target_path, "r", encoding="utf-8") as handle:
                translated = json.load(handle)

        self.assertEqual(translated["title"], "ja:Hello")
        self.assertEqual(translated["details"]["subtitle"], "ja:World")
        self.assertEqual(translated["details"]["nested"]["deep"], "ja:Value")
        self.assertEqual(translated["count"], 3)


if __name__ == "__main__":
    unittest.main()
