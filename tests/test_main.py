import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import shutil
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import process_app, main


class TestMain(unittest.TestCase):
    def setUp(self):
        # テスト用のディレクトリを作成
        self.test_dirs = ["temp", "translate_rp", "logs"]
        for dir_name in self.test_dirs:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

        # テスト用のモックページを作成
        self.mock_page = MagicMock()

    def tearDown(self):
        # テスト用のディレクトリを削除
        for dir_name in self.test_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

    @patch("main.notification")
    def test_process_app_with_valid_paths(self, mock_notification):
        # 正常なファイルパスでのテスト
        test_paths = ["test1.jar", "test2.jar"]
        test_names = ["test1", "test2"]

        with patch("main.file_utils") as mock_file_utils:
            mock_file_utils.gen_pack_dir.return_value = 0
            with patch("main.translation_module") as mock_translation:
                mock_translation.translate_in_thread.return_value = 0

                with self.assertRaises(SystemExit):
                    process_app(test_paths, test_names, self.mock_page)

                # 各モックが正しく呼ばれたことを確認
                mock_file_utils.unzip_jar.assert_called()
                mock_file_utils.gen_pack_dir.assert_called_once()
                mock_translation.translate_in_thread.assert_called_once()
                mock_notification.notify.assert_called_once()

    @patch("main.file_utils")
    def test_process_app_with_gen_pack_dir_failure(self, mock_file_utils):
        # pack_dir生成失敗時のテスト
        test_paths = ["test.jar"]
        test_names = ["test"]
        mock_file_utils.gen_pack_dir.return_value = 1

        with self.assertRaises(SystemExit) as cm:
            process_app(test_paths, test_names, self.mock_page)
        self.assertEqual(cm.exception.code, 1)

    @patch("main.ft.app")
    @patch("main.file_utils")
    def test_main_function(self, mock_file_utils, mock_ft_app):
        # main関数のテスト
        main()

        # init_dirが2回呼ばれることを確認
        self.assertEqual(mock_file_utils.init_dir.call_count, 2)
        # flet.appが呼ばれることを確認
        mock_ft_app.assert_called_once()

    def test_logging_setup(self):
        # ロギング設定のテスト
        logger = logging.getLogger("main")
        self.assertTrue(logger.handlers)
        self.assertEqual(logger.level, logging.DEBUG)

        # ログファイルが作成されることを確認
        self.assertTrue(os.path.exists("logs"))


if __name__ == "__main__":
    unittest.main()
