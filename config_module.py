
# 指定したフォルダとその中身以外のファイルとフォルダを削除する、langフォルダの処理をするための関数
import os, logging
logger = logging.getLogger(__name__)


def remove_other_files(path):
    """
    指定したフォルダとその中身以外のファイルとフォルダを削除する、langフォルダの処理をするための関数

    Args:
        path (str): 削除するフォルダのパス
    """
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if d != "lang":
                os.rmdir(os.path.join(root, d))
        for f in files:
            if f != "pack.mcmeta":
                os.remove(os.path.join(root, f))
    return