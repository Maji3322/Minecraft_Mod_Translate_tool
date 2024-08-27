""" 作成: 2024/04/05

# このバージョンでは、モジュール化を行うことを目標とする。

<予定している機能改善>
・全体の翻訳完了までの予想時間を表示
・modのなかにあるmodも翻訳できるようにしたい。(aaa.jar/META-INF/jars/xxx.jar/assets/yyy/lang/en_us.json)
・自動アップデート機能

<バグ・不具合>
・ファイル名が長すぎると謎のエラーが起きてしまう...(try-exceptで回避したけども...)
"""

import os, sys, glob, subprocess
from googletrans import Translator
import logging.handlers
import flet as ft
import search_files, translation_module, file_utils, gui_module
from plyer import notification

# ログの設定
logger = logging.getLogger(__name__)  # ロガーを取得
logger.setLevel(logging.DEBUG)  # ログレベルの設定

# ログファイルを出力するディレクトリが存在しない場合は作成する
if not os.path.exists("logs"):
    os.mkdir("logs")
rh = logging.handlers.RotatingFileHandler(filename='logs/mcmt.log', maxBytes=100000, backupCount=3)  # ログローテーションを設定
logger.addHandler(rh)  # ログハンドラーを追加
logger.debug("===== START =====")  # ログを出力

# Google翻訳APIを使うための初期設定
translator = Translator()


def validate_path(path, page):
    if not os.path.isabs(path):
        gui_module.err_dlg(page, "エラー", "絶対パスを指定してください。")
        raise ValueError("絶対パスを指定してください。")
    if ".." in path:
        gui_module.err_dlg(page, "エラー", "不正なパスが含まれています。")
        raise ValueError("不正なパスが含まれています。")
    return path


def cleanup_and_exit():
    # リソースのクリーンアップを行う
    logger.debug("===== END =====")
    logging.shutdown()
    sys.exit()


def process_app(file_paths, file_names, page):
    try:
        logger.info("LOG: ファイルの処理を開始: %s", file_names)
        for f in file_paths:
            file_utils.unzip_jar(f)  # jarファイルをtempに解凍

        json_files = glob.glob(validate_path(os.path.join("temp", '**', 'en_us.json'), page), recursive=True)
        logger.info("json_files: %s ", json_files)
        file_utils.delete_files_except("temp", json_files)
        if file_utils.gen_pack_dir(str(gui_module.return_pack_format()), page, json_files) == 0:
            logger.info("INFO: translate_rpフォルダを生成しました。")
        else:
            logger.error("ERROR: translate_rpフォルダの生成に失敗しました。")
            cleanup_and_exit()

        file_utils.copy_assets_folders("temp", json_files)
        lang_file_paths = search_files.search_lang_file()

        if translation_module.translate_in_thread(lang_file_paths, page) == 0:
            logger.info("INFO: 翻訳が完了しました。")
            gui_module.err_dlg(page, "完了","全ての翻訳が完了しました。")
            notification.notify(
                title="翻訳完了",
                message="すべての翻訳が完了しました。",
                app_name="MC-MOD Translating tool",
                app_icon="resources/icon.ico"
            )
            gui_module.confirm_open_folder(page, "確認", "作成されたリソースパックのフォルダを開きますか？", subprocess.Popen(["explorer", "translate_rp"]), check=True)
            def destroy(e):
                page.window_destroy()
            destroy(None)
            cleanup_and_exit()
        else:
            logger.error("ERROR: 翻訳に失敗しました。")
            gui_module.err_dlg(page, "エラー","翻訳に失敗しました。")
            cleanup_and_exit()
    except Exception as e:
        logger.error("ERROR: %s", str(e))
        gui_module.err_dlg(page, "エラー", f"エラーが発生しました: {str(e)}")
        cleanup_and_exit()


def main():
    file_utils.init_dir("temp")
    file_utils.init_dir("translate_rp")
    ft.app(target=gui_module.start_gui, assets_dir="assets")


if __name__ == "__main__":
    main()
