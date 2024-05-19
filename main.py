""" 作成: 2024/04/05

# このバージョンでは、モジュール化を行うことを目標とする。


<予定している機能改善>
・全体の翻訳完了までの予想時間を表示
・modのなかにあるmodも翻訳できるようにしたい。(aaa.jar/META-INF/jars/xxx.jar/assets/yyy/lang/en_us.json)
・自動アップデート機能

<バグ・不具合>
・ファイル名が長すぎると謎のエラーが起きてしまう...(try-exceptで回避したけども...)
"""

# すべての変数名の重複を回避するために、関数ごとに変数のスコープを分ける。

from plyer import notification

import os, sys, glob

from googletrans import Translator
import logging.handlers
import flet as ft

import search_files, translation_module, file_utils, gui_module

# ログの設定
logger = logging.getLogger(__name__) # ロガーを取得
logger.setLevel(logging.DEBUG) # ログレベルの設定

# ログファイルを出力するディレクトリが存在しない場合は作成する
if not os.path.exists("logs"):
    os.mkdir("logs")
rh = logging.handlers.RotatingFileHandler(filename='logs/mcmt.log', maxBytes=100000, backupCount=3) # ログローテーションを設定
logger.addHandler(rh) # ログハンドラーを追加
logger.debug("===== START =====") # ログを出力

# Google翻訳APIを使うための初期設定
translator = Translator()

def process_app(file_paths, file_names, page):
    main_page = page
    print(file_paths)
    for f in file_paths:
        file_utils.unzip_jar(f)  # jarファイルをtempに解凍

    # tempの中からjarファイルを探し、またそれを解凍する。
    # 解凍したファイルのMETA-INFの中を探索し、その中のjarファイルを解凍する。
    # 解凍したファイルのMETA-INFの中にjarファイルが無くなるまで繰り返す。
    # ということがしたかったのだが、うまくいかなかったので、一旦保留。一回だけ解凍することにする。
    
    # tempフォルダの中からlangファイルを探し、そのlangファイルのパス上にあるフォルダ以外のフォルダとファイルをtempから削除する
    json_files = glob.glob(os.path.join("temp", '**', 'en_us.json'), recursive=True)
    # en_us.jsonファイルのパス上にあるフォルダ以外を削除
    print(f"json_files: {json_files}")
    file_utils.delete_files_except("temp", json_files)
    # リソースパックのフォルダを作成、pack.mcmetaを作成
    if file_utils.gen_pack_dir(str(gui_module.return_pack_format()), page, json_files) == 0:
        logger.info("LOG: translate_rpフォルダを生成しました。")
    else:
        logger.error("ERROR: translate_rpフォルダの生成に失敗しました。")
        sys.exit(1)
    # assets以下をtranslate_rpにコピー
    file_utils.copy_assets_folders("temp", json_files)
    
    # en_us.jsonファイルのパスを取得
    lang_file_paths = search_files.search_lang_file()

    # 翻訳を実行
    if translation_module.translate_in_thread(lang_file_paths, page) == 0:
        logger.info("LOG: 翻訳が完了しました。")
        gui_module.err_dlg(page, "完了","全ての翻訳が完了しました。")
        # 翻訳完了を通知
        notification.notify(
            title="翻訳完了",
            message="すべての翻訳が完了しました。",
            app_name="MC-MOD Translating tool",
            app_icon="resources/icon.ico"
            )
        # translate_rpフォルダの上のフォルダを開く
        os.startfile(os.path.dirname("translate_rp"))
        def destroy(e):
            page.window_destroy()
        destroy(None)
        # プログラムを終了する
        sys.exit()

    else:
        logger.error("ERROR: 翻訳に失敗しました。")
        gui_module.err_dlg(page, "エラー","翻訳に失敗しました。")
        sys.exit(1)

def main():
    file_utils.init_dir("temp")
    file_utils.init_dir("translate_rp")
    ft.app(target=gui_module.start_gui, assets_dir="assets")
    


if __name__ == "__main__":
    main()