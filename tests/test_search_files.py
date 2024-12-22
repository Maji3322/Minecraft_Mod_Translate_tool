import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search_files import search_lang_file, search_jar_files

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSearchFiles(unittest.TestCase):
    def setUp(self):
        # テスト用のディレクトリ構造を作成
        os.makedirs("translate_rp/test1", exist_ok=True)
        os.makedirs("translate_rp/test2", exist_ok=True)
        os.makedirs("temp/test1", exist_ok=True)

        # テストファイルを作成
        with open("translate_rp/test1/en_us.json", "w") as f:
            f.write("{}")
        with open("translate_rp/test2/en_us.json", "w") as f:
            f.write("{}")
        with open("translate_rp/test2/ja_jp.json", "w") as f:
            f.write("{}")
        with open("temp/test1/test.jar", "w") as f:
            f.write("")

    def test_search_lang_file(self):
        # 翻訳が必要なファイルのパスを取得
        result = search_lang_file()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # ja_jp.jsonがないen_us.jsonは1つだけ
        self.assertTrue(result[0].endswith("test1/en_us.json"))

    def test_search_jar_files(self):
        # JARファイルのパスを取得
        result = search_jar_files()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0][0].endswith("test.jar"))

    def tearDown(self):
        # テスト用のファイルとディレクトリを削除
        for path in ["translate_rp", "temp"]:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(path)


if __name__ == "__main__":
    unittest.main()
