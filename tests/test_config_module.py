import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_module import remove_other_files


class TestConfigModule(unittest.TestCase):
    def setUp(self):
        # テスト用のディレクトリ構造を作成
        self.test_dir = "test_directory"
        os.makedirs(os.path.join(self.test_dir, "lang"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "other_dir"), exist_ok=True)

        # テストファイルを作成
        with open(os.path.join(self.test_dir, "pack.mcmeta"), "w") as f:
            f.write("test")
        with open(os.path.join(self.test_dir, "delete_me.txt"), "w") as f:
            f.write("test")

    def test_remove_other_files(self):
        # 関数を実行
        remove_other_files(self.test_dir)

        # 期待する結果をテスト
        self.assertTrue(
            os.path.exists(os.path.join(self.test_dir, "lang"))
        )  # langフォルダは残る
        self.assertTrue(
            os.path.exists(os.path.join(self.test_dir, "pack.mcmeta"))
        )  # pack.mcmetaは残る
        self.assertFalse(
            os.path.exists(os.path.join(self.test_dir, "other_dir"))
        )  # 他のフォルダは削除される
        self.assertFalse(
            os.path.exists(os.path.join(self.test_dir, "delete_me.txt"))
        )  # 他のファイルは削除される

    def test_empty_directory(self):
        # 空のディレクトリでテスト
        empty_dir = "empty_test_directory"
        os.makedirs(empty_dir, exist_ok=True)
        remove_other_files(empty_dir)
        self.assertTrue(os.path.exists(empty_dir))  # ディレクトリ自体は残る

    def test_nonexistent_directory(self):
        # 存在しないディレクトリでテスト
        with self.assertRaises(FileNotFoundError):
            remove_other_files("nonexistent_directory")
            def test_remove_other_files_with_nested_directories(self):
                # ネストされたディレクトリ構造を作成
                nested_dir = os.path.join(self.test_dir, "nested")
                os.makedirs(nested_dir, exist_ok=True)
                with open(os.path.join(nested_dir, "nested_file.txt"), "w") as f:
                    f.write("test")

                # 関数を実行
                remove_other_files(self.test_dir)

                # 期待する結果をテスト
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "lang")))  # langフォルダは残る
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "pack.mcmeta")))  # pack.mcmetaは残る
                self.assertFalse(os.path.exists(os.path.join(self.test_dir, "nested")))  # ネストされたフォルダは削除される
                self.assertFalse(os.path.exists(os.path.join(nested_dir, "nested_file.txt")))  # ネストされたファイルは削除される

            def test_remove_other_files_with_only_lang_and_pack_mcmeta(self):
                # langフォルダとpack.mcmetaファイルのみを持つディレクトリでテスト
                remove_other_files(self.test_dir)

                # 期待する結果をテスト
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "lang")))  # langフォルダは残る
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "pack.mcmeta")))  # pack.mcmetaは残る

            def test_remove_other_files_with_symlinks(self):
                # シンボリックリンクを作成
                symlink_path = os.path.join(self.test_dir, "symlink")
                os.symlink(os.path.join(self.test_dir, "pack.mcmeta"), symlink_path)

                # 関数を実行
                remove_other_files(self.test_dir)

                # 期待する結果をテスト
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "lang")))  # langフォルダは残る
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "pack.mcmeta")))  # pack.mcmetaは残る
                self.assertFalse(os.path.exists(symlink_path))  # シンボリックリンクは削除される

            def test_remove_other_files_with_hidden_files(self):
                # 隠しファイルを作成
                hidden_file_path = os.path.join(self.test_dir, ".hidden_file")
                with open(hidden_file_path, "w") as f:
                    f.write("test")

                # 関数を実行
                remove_other_files(self.test_dir)

                # 期待する結果をテスト
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "lang")))  # langフォルダは残る
                self.assertTrue(os.path.exists(os.path.join(self.test_dir, "pack.mcmeta")))  # pack.mcmetaは残る
                self.assertFalse(os.path.exists(hidden_file_path))  # 隠しファイルは削除される
    def tearDown(self):
        # テスト用のファイルとディレクトリを削除
        if os.path.exists(self.test_dir):
            for root, dirs, files in os.walk(self.test_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.test_dir)

        if os.path.exists("empty_test_directory"):
            os.rmdir("empty_test_directory")


if __name__ == "__main__":
    unittest.main()
