"""
指定したフォルダとその中身以外のファイルとフォルダを削除する、langフォルダの処理をするための関数
"""

import logging
import os
import shutil

logger = logging.getLogger(__name__)

def remove_other_files(path):
    """
    指定されたディレクトリ内の `lang` フォルダとその中身のファイル + `pack.mcmeta` という名前のファイル以外のすべてのファイルを削除する。

    ### 削除される例
    - 'lang' という名前ではないフォルダ
    - 'lang' フォルダ内のファイル
    - 'pack.mcmeta' 以外のファイル

    Args:
        path (str): 実行するルートディレクトリ

    Returns:
        0: 正常終了
    """
    try:
        for root, dirs, files in os.walk(path, topdown=True):
            for d in dirs:
                if d != "lang":
                    shutil.rmtree(os.path.join(root, d))
            for f in files:
                if f != "pack.mcmeta":
                    os.remove(os.path.join(root, f))
        return 0
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1
