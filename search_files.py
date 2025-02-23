# NOTE: このプログラムは、en_us.jsonファイルを探し、そのパスを返す

import glob
import logging.handlers
import os

# ログの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# ファイルハンドラーの設定
rh = logging.handlers.RotatingFileHandler(
    filename="logs/search_files.log", maxBytes=100000, backupCount=3, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
rh.setFormatter(formatter)
logger.addHandler(rh)

# コンソールハンドラーの設定
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def search_lang_file():
    """
    translate_rpフォルダ内で、同階層にja_jp.jsonが存在しないen_us.jsonファイルのパスを返します。

    Returns:
        list or str: 翻訳対象のen_us.jsonファイルのパスのリスト。
                    対象ファイルがない場合は状態を示す文字列を返します。
    """
    logger.info("search_lang_file関数を開始します。")

    # すべてのen_us.jsonファイルを検索
    en_us_json_paths = glob.glob("translate_rp/**/en_us.json", recursive=True)
    if not en_us_json_paths:
        logger.info("en_us.jsonファイルが見つかりません。翻訳をスキップします。")
        return "No lang folder"

    # 翻訳が必要なファイルのパスを保存するリスト
    need_translation_paths = []

    # 各en_us.jsonについて、ja_jp.jsonの存在確認
    for en_us_path in en_us_json_paths:
        if not en_us_path:
            continue

        # 同じディレクトリ内のja_jp.jsonのパスを取得
        ja_jp_json_path = os.path.join(os.path.dirname(en_us_path), "ja_jp.json")
        print(ja_jp_json_path)

        # ja_jp.jsonが存在しない場合のみ翻訳対象とする
        if not os.path.exists(ja_jp_json_path):
            logger.info(
                "「%s」に対応するja_jp.jsonが見つからないため、翻訳対象とします。",
                en_us_path,
            )
            need_translation_paths.append(en_us_path)
        else:
            logger.info(
                "「%s」に対応するja_jp.jsonが存在するため、スキップします。", en_us_path
            )

    if not need_translation_paths:
        logger.info(
            "すべてのen_us.jsonに対応するja_jp.jsonが存在します。翻訳は不要です。"
        )
        return []

    return need_translation_paths


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
