import unittest, sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from file_utils import (
    init_dir,
    gen_pack_dir,
    lang_remove_other_files,
    unzip_jar,
    delete_files_except,
    copy_assets_folders,
)



class TestFileUtils(unittest.TestCase):
    def setUp(self):
        # テスト用のディレクトリを作成
        self.test_dir = "test_temp"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def tearDown(self):
        # テスト用のディレクトリを削除
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("translate_rp"):
            shutil.rmtree("translate_rp")

    def test_init_dir(self):
        # 新規ディレクトリの作成をテスト
        test_path = os.path.join(self.test_dir, "new_dir")
        init_dir(test_path)
        self.assertTrue(os.path.exists(test_path))

        # 既存ディレクトリの初期化をテスト
        with open(os.path.join(test_path, "test.txt"), "w") as f:
            f.write("test")
        init_dir(test_path)
        self.assertEqual(len(os.listdir(test_path)), 0)

    def test_gen_pack_dir(self):
        # pack.mcmetaの生成をテスト
        json_files = [
            "assets/minecraft/lang/en_us.json",
            "assets/mymod/lang/en_us.json",
        ]
        result = gen_pack_dir("8", None, json_files)
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists("translate_rp/pack.mcmeta"))

        # バージョン未指定のテスト
        result = gen_pack_dir("", None, json_files)
        self.assertEqual(result, 1)

    def test_lang_remove_other_files(self):
        # テスト用のディレクトリ構造を作成
        test_structure = os.path.join(self.test_dir, "assets/test")
        os.makedirs(os.path.join(test_structure, "lang"))
        os.makedirs(os.path.join(test_structure, "textures"))

        with open(os.path.join(test_structure, "test.txt"), "w") as f:
            f.write("test")

        lang_remove_other_files(test_structure)
        self.assertTrue(os.path.exists(os.path.join(test_structure, "lang")))
        self.assertFalse(os.path.exists(os.path.join(test_structure, "textures")))
        self.assertFalse(os.path.exists(os.path.join(test_structure, "test.txt")))


if __name__ == "__main__":
    unittest.main()
