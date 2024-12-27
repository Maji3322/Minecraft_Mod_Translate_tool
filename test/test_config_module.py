""" config_module.pyのテストコード """

import os
import pytest
from config_module import remove_other_files


@pytest.fixture
def test_dir(tmp_path):
    """
    テスト用のディレクトリを作成する

    Args:
        tmp_path: テスト用のディレクトリ

    Returns:
        test_directory: テスト用のディレクトリ
    """
    # テスト用の一時ディレクトリを作成
    test_directory = tmp_path / "test_dir"
    test_directory.mkdir()

    # 必要なファイルとディレクトリを作成
    (test_directory / "pack.mcmeta").touch()
    (test_directory / "other").mkdir()
    (test_directory / "test.txt").touch()
    (test_directory / "lang").mkdir()
    (test_directory / "lang" / "en_us.json").touch()

    return test_directory

def test_remove_other_files(test_dir):
    """
    remove_other_files関数のテスト

    Args:
        test_dir: テスト用のディレクトリ

    Returns:
        None
    """
    # 関数を実行
    remove_other_files(test_dir)

    # langディレクトリとpack.mcmetaだけが残っているか確認
    assert os.path.exists(test_dir / "pack.mcmeta")

    # 他のファイルとディレクトリが削除されているか確認
    assert not os.path.exists(test_dir / "other")
    assert not os.path.exists(test_dir / "test.txt")

    # langディレクトリの中身は残っているか確認
    assert os.path.exists(test_dir / "lang" / "en_us.json")


def test_remove_other_files_empty_dir(tmp_path):
    """
    remove_other_files関数のテスト

    Args:
        tmp_path: テスト用のディレクトリ

    Returns:
        None
    """
    # 空のディレクトリでテスト
    tmp_path.mkdir(exist_ok=True)  # 空のディレクトリを作成
    remove_other_files(tmp_path)
    assert os.path.exists(tmp_path)


def test_remove_other_files_return_value(test_dir):
    """
    remove_other_files関数の戻り値のテスト

    Args:
        target_dir: テスト用のディレクトリ

    Returns:
        None
    """
    # 戻り値が0であることを確認
    result = remove_other_files(test_dir)
    assert result == 0
