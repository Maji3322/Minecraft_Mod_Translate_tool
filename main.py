"""
<予定している機能改善>
・全体の翻訳完了までの予想時間を表示
・自動バージョンアップデート機能（再ダウンロード不要にする。どうやってやるのかはわからないけども...）

<バグ・不具合>
・ファイル名が長すぎると謎のエラーが起きてしまう...(try-exceptで回避したけども...)
・マージがうまくいっていない気がする。
"""

# すべての変数名の重複を回避するために、関数ごとに変数のスコープを分ける。

import glob
import logging.handlers
import os
import sys
import time

import flet as ft
from googletrans import Translator
from plyer import notification

import file_utils
import gui_module
import search_files
import translation_module

# ログの設定
logger = logging.getLogger(__name__)  # ロガーを取得
logger.setLevel(logging.DEBUG)  # ログレベルの設定

# ログファイルを出力するディレクトリが存在しない場合は作成する
if not os.path.exists("logs"):
    os.mkdir("logs")
rh = logging.handlers.RotatingFileHandler(
    filename="logs/mcmt.log", maxBytes=100000, backupCount=3, encoding="utf-8"
)  # ログローテーションを設定
logger.addHandler(rh)  # ログハンドラーを追加
logger.info("===== START =====")  # ログを出力

# Google翻訳APIを使うための初期設定
translator = Translator()

# ログの設定をコンソールにも出力するように設定
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def process_app(file_paths, file_names, page):
    """
    指定されたファイルパスとファイル名を処理し、翻訳を実行する関数。

    Args:
        file_paths (list): ファイルのパスのリスト
        file_names (list): ファイル名のリスト
        page (tkinter.Tk): ページのインスタンス

    Returns:
        None
    """
    logger.info("===== process_app関数を開始します。 =====")
    logger.info("file_paths: %s", file_paths)
    logger.info("file_names: %s", file_names)
    logger.info("page: %s", page)

    # 翻訳開始前にUI要素を隠す
    gui_module.hide_selection_ui(page)

    # ローディングインジケータを非表示にする
    gui_module.hide_loading(page)

    # temp と translate_rp を同時に初期化
    file_utils.init_dir("temp")
    file_utils.init_dir("translate_rp")
    logger.info("tempディレクトリとtranslate_rpディレクトリを同時に初期化しました。")

    # 解凍進捗表示UI作成
    extract_pb, extract_info = gui_module.make_extract_progress(page)
    total_files = len(file_paths)

    unzipped_file_paths = []
    for i, f in enumerate(file_paths):
        # 進捗表示更新
        current_file = i + 1
        file_name = os.path.basename(f)
        gui_module.update_extract_progress(
            extract_pb, current_file, total_files, extract_info, page, file_name
        )

        # jarファイル解凍
        unzipped_file_paths.append(file_utils.recursive_unzip_jar(f))

    # 解凍完了表示の更新とプログレスバーの非表示
    extract_info.value = "解凍完了"
    page.update()
    # 少し待機して完了メッセージを表示
    time.sleep(1)
    # 解凍進捗表示を非表示
    gui_module.hide_extract_progress(page)

    # 以降の処理（en_us.jsonファイルの検索など）を続行

    # tempの中からjarファイルを探し、またそれを解凍する。
    # 解凍したファイルのMETA-INFの中を探索し、その中のjarファイルを解凍する。
    # 解凍したファイルのMETA-INFの中にjarファイルが無くなるまで繰り返す。

    # tempフォルダの中からlangファイルを探し、そのlangファイルのパス上にあるフォルダ以外のフォルダとファイルをtempから削除する
    # tempフォルダ内のすべてのサブディレクトリから英語の言語ファイルを検索

    # 解凍した中にあるすべてのen_us.jsonファイルのパスのリストを取得
    us_en_json_files = glob.glob(
        os.path.join("temp", "**", "en_us.json"),  # en_us.jsonファイルを検索
        recursive=True,  # 再帰的に検索
    )

    logger.log(logging.DEBUG, "Detected en_us.json files: %s", us_en_json_files)

    # en_us.jsonファイルのパス上にあるフォルダ以外を削除
    # en_us.jsonファイルと、同じディレクトリにあるja_jp.jsonのパスのリストを作成
    files_to_keep = []
    for us_en_json_file in us_en_json_files:
        files_to_keep.append(us_en_json_file)
        # 同じディレクトリにあるja_jp.jsonも保持対象に追加
        ja_jp_file = os.path.join(os.path.dirname(us_en_json_file), "ja_jp.json")
        if os.path.exists(ja_jp_file):
            files_to_keep.append(ja_jp_file)

    # 保持するファイル以外を削除
    file_utils.clean_directory("temp", files_to_keep)
    # リソースパックのフォルダを作成、pack.mcmetaを作成
    if (
        file_utils.gen_pack_dir(
            str(gui_module.return_pack_format()), page, us_en_json_files
        )
        == 0
    ):
        logger.info("translate_rpフォルダを生成しました。")
    else:
        logger.error("translate_rpフォルダの生成に失敗しました。")
        sys.exit(1)
    # assets以下をtranslate_rpにコピー
    file_utils.copy_assets_folders("temp", us_en_json_files)

    # en_us.jsonファイルのパスを取得
    lang_file_paths = search_files.search_lang_file()

    # 翻訳を実行
    if translation_module.translate_in_thread(lang_file_paths, page) == 0:
        logger.info("翻訳が完了しました。")
        gui_module.err_dlg(page, "完了", "全ての翻訳が完了しました。")
        # 翻訳完了を通知
        notification.notify(
            title="翻訳完了",
            message="すべての翻訳が完了しました。",
            app_name="MC-MOD Translating tool",
            app_icon="resources/icon.ico",
        )
        # translate_rpフォルダの上のフォルダを開く
        os.startfile(os.path.dirname("translate_rp"))

        def destroy():
            page.window_destroy()

        destroy()
        # プログラムを終了する
        sys.exit()

    else:
        logger.error("翻訳に失敗しました。")
        gui_module.err_dlg(page, "エラー", "翻訳に失敗しました。")
        sys.exit(1)


def main(page: ft.Page):
    """
    メインアプリケーションのエントリーポイント
    """
    try:
        logger.info("Initializing GUI")
        logger.debug("Page state before GUI initialization: %s", page)
        from gui_module import start_gui  # 循環参照を避けるためにここでインポート

        start_gui(page)
        logger.debug("Page state after GUI initialization: %s", page)
        logger.info("GUI initialized successfully")
    except Exception as e:
        logger.error("Error initializing GUI: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    # Fletアプリケーションの開始
    ft.app(target=main, assets_dir="assets")
