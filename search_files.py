# NOTE: このプログラムは、en_us.jsonファイルを探し、そのパスを返す

import glob
import logging.handlers
import os

logger = logging.getLogger(__name__)


def search_lang_file():
    """
    translate_rpにあり、同階層にja_jp.jsonが存在しないen_us.jsonファイルのパスを返します。

    Returns:
        list: 翻訳対象のen_us.jsonファイルのパス。
    """
    logger.info("search_lang_file関数を開始します。")
    en_us_json_paths = glob.glob("translate_rp/**/en_us.json", recursive=True)
    if not en_us_json_paths:
        logger.info("No lang folder found. Skipping translation.")
        return "No lang folder"

    served_en_us_json_paths = []
    for i in en_us_json_paths:
        if i:
            ja_jp_json_path = os.path.join(os.path.dirname(i), "ja_jp.json")
            print(f"ja_jp_json_path: {ja_jp_json_path}")
            if not os.path.exists(ja_jp_json_path):
                logger.info(
                    "LOG: en_us.jsonが見つかり、ja_jp.jsonがないため翻訳を開始します。"
                )
                served_en_us_json_paths.append(i)
            else:
                logger.info("ja_jp.jsonが見つかったので、翻訳をスキップします。")
        else:
            logger.info(
                "LOG: langフォルダが見つからなかったので、翻訳をスキップします。"
            )

    if not served_en_us_json_paths:
        logger.info("All en_us.json have matching ja_jp.json. Skipping translation.")
        return "exist ja_jp.json"

    return served_en_us_json_paths


def search_jar_files():
    """
    tempフォルダの中からjarファイルをフォルダの中のフォルダも含め、
    最終的な祖先がtempであるjarファイルのパスを配列で返す
    Args:
        None
    """
    logger.info("search_jar_files関数を開始します。")
    jar_files = []
    jar_files.append(
        glob.glob("temp/**/*.jar", recursive=True)
    )  # tempフォルダの中からjarファイルを探してリストに追加
    print(jar_files)
    return jar_files
