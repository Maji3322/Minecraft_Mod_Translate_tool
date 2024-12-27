"""
このプログラムは、en_us.jsonファイルを探し、そのパスを返す
"""

import glob
import logging.handlers
import os

logger = logging.getLogger(__name__)

def search_lang_file():
    """
    `translate_rp`の中にあり、同階層に`ja_jp.json`が存在しない`en_us.json`ファイルのパスを返します。

    Args:
        None

    Returns:
        list: 翻訳対象のen_us.jsonファイルのパス。
    """
    en_us_json_file_locations = glob.glob("translate_rp/**/en_us.json", recursive=True)
    en_us_files_missing_ja_jp = []
    for i in en_us_json_file_locations:
        if i:
            ja_jp_json_path = os.path.join(os.path.dirname(i), "ja_jp.json")
            print(f"ja_jp_json_path: {ja_jp_json_path}")
            if not os.path.exists(ja_jp_json_path):
                logger.info(
                    "LOG: en_us.jsonが見つかり、ja_jp.jsonがないため翻訳を開始します。"
                )
                en_us_files_missing_ja_jp.append(i)
            else:
                logger.info("LOG: ja_jp.jsonが見つかったので、翻訳をスキップします。")
        else:
            logger.info(
                "LOG: langフォルダが見つからなかったので、翻訳をスキップします。"
            )
    return en_us_files_missing_ja_jp

def search_jar_files():
    """
    tempフォルダの中からjarファイルをフォルダの中のフォルダも含め、
    最終的な祖先がtempであるjarファイルのパスを配列で返す
    Args:
        None
    """
    jar_files = []
    jar_files.append(
        glob.glob("temp/**/*.jar", recursive=True)
    )  # tempフォルダの中からjarファイルを探してリストに追加
    print(jar_files)
    return jar_files
