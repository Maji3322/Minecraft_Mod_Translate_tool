import unittest
import os
import sys
import json
import flet as ft
from unittest.mock import MagicMock, patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from translation_module import translate_json, translate_in_thread


class TestTranslationModule(unittest.TestCase):
    def setUp(self):
        # テスト用のディレクトリとファイルを作成
        os.makedirs("test_lang", exist_ok=True)
        self.test_json = {
            "test.key1": "Hello",
            "test.key2": "World",
            "test.nested": {"key3": "Nested hello", "key4": "Nested world"},
        }
        with open("test_lang/en_us.json", "w", encoding="utf-8") as f:
            json.dump(self.test_json, f)

        # fletのページをモック
        self.mock_page = MagicMock()

    def test_translate_json_success(self):
        # 翻訳が成功するケース
        with patch("translation_module.Translator") as mock_translator:
            # 翻訳結果のモックを設定
            mock_translator.return_value.translate.return_value = MagicMock(
                text="こんにちは"
            )

            result = translate_json("test_lang/en_us.json", self.mock_page)

            # 戻り値が0（成功）であることを確認
            self.assertEqual(result, 0)

            # ja_jp.jsonが作成されていることを確認
            self.assertTrue(os.path.exists("test_lang/ja_jp.json"))

    def test_translate_json_failure(self):
        # 翻訳が失敗するケース
        with patch("translation_module.Translator") as mock_translator:
            mock_translator.return_value.translate.side_effect = Exception(
                "Translation failed"
            )

            result = translate_json("test_lang/en_us.json", self.mock_page)

            # 戻り値が1（失敗）であることを確認
            self.assertEqual(result, 1)

    def test_translate_in_thread_no_lang_folder(self):
        # langフォルダが見つからないケース
        result = translate_in_thread("No lang folder", self.mock_page)
        self.assertIsNone(result)

    def test_translate_in_thread_existing_translation(self):
        # ja_jp.jsonが既に存在するケース
        result = translate_in_thread("exist ja_jp.json", self.mock_page)
        self.assertIsNone(result)

    def test_translate_in_thread_success(self):
        # 正常に翻訳が実行されるケース
        with patch("translation_module.translate_json") as mock_translate:
            mock_translate.return_value = 0
            result = translate_in_thread(["test_lang/en_us.json"], self.mock_page)
            self.assertEqual(result, 0)

    def tearDown(self):
        # テストファイルとディレクトリの削除
        if os.path.exists("test_lang"):
            for file in os.listdir("test_lang"):
                os.remove(os.path.join("test_lang", file))
            os.rmdir("test_lang")


if __name__ == "__main__":
    unittest.main()
