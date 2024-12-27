"""
# NOTE: guiの処理をまとめたモジュール
# NOTE: CTKからFletに移行する
"""

import logging
import os
import sys
import time
import webbrowser

import flet as ft
import pyperclip

import main

logger = logging.getLogger(__name__)


def err_dlg(page: ft.Page, err_title: str, err_msg: str):
    """
    指定されたエラーメッセージを含むエラーダイアログを表示します。
    Args:
        page (ft.Page): エラーダイアログが表示されるページオブジェクトです。
        err_msg (str): ダイアログに表示されるエラーメッセージです。
    """

    def close_dlg(e):  # eは使用しないが、仮の引数が必要
        err_dlg.open = False
        page.update()

    def dlg_open():
        page.dialog = err_dlg
        err_dlg.open = True
        page.update()

    err_dlg = ft.AlertDialog(
        title=ft.Text(err_title),
        modal=True,
        content=ft.Text(err_msg),
        actions=[
            ft.TextButton("閉じる", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dlg_open()


def end_dlg(page: ft.Page, end_msg: str):
    """
    指定されたエラーメッセージを含むエラーダイアログを表示します。
    Args:
        page (ft.Page): エラーダイアログが表示されるページオブジェクトです。
        err_msg (str): ダイアログに表示されるエラーメッセージです。
    """

    def close_dlg(e):  # eは使用しないが、仮の引数が必要
        err_dlg.open = False
        page.update()
        sys.exit(0)

    def dlg_open():
        page.dialog = err_dlg
        err_dlg.open = True
        page.update()

    err_dlg = ft.AlertDialog(
        title=ft.Text("翻訳完了"),
        modal=True,
        content=ft.Text(end_dlg),
        actions=[
            ft.TextButton("閉じる", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dlg_open()


def select_file(e: ft.FilePickerResultEvent, page: ft.Page):
    """
    ファイル選択ダイアログを表示し、選択されたファイルのパスをGUI上に表示する。
    選択されたファイルに対して、ready_translate関数を実行し、翻訳処理を行う。
    翻訳処理が完了したら、tempフォルダを初期化し、最後のファイルの翻訳が完了したら、アプリを終了する。

    Returns:
        選択されたファイルのパスのリスト
    """

    global file_names
    file_paths = [
        file.path for file in e.files
    ]  # ファイル選択ダイアログで選択されたファイルのパスを取得
    file_names = list(
        [os.path.basename(file_name) for file_name in file_paths]
    )  # 選択されたファイルの名前を取得

    # ファイルのパスをボタンの右側に表示
    ft.Text(file_paths, width=300, style=ft.TextStyle(bgcolor="#2b2e31"))
    selected_files.value = (
        ", ".join(map(lambda f: f.name, e.files))
        if e.files
        else "キャンセルされました!"
    )
    selected_files.update()

    # 翻訳処理を別のスレッドで実行
    if not file_paths == []:  # ファイルが選択された場合
        main.process_app(file_paths, file_names, page)
    else:
        # file_pathsが空の場合、エラーメッセージを表示して関数を終了
        err_dlg(page, "エラー", "jarファイルが見つかりませんでした。")


def select_file_from_clipboard(page: ft.Page):
    """
    pyperclipを使用してクリップボードからファイルパスを取得し、その中のjarファイルをリストとして取得する関数。
    取得したファイルパスはプリントされる。
    """
    global file_names
    file_paths = []

    # クリップボードにあるmodsフォルダーのパスを取得
    mods_path = pyperclip.paste()

    # mods_pathの両端にあるダブルクォーテーションを削除
    mods_path = mods_path.replace('"', "")

    # modsフォルダーのパスが存在するか確認
    if os.path.exists(mods_path):
        # modsフォルダーのパスが存在する場合、その中のjarファイルをリストとして取得
        try:
            file_paths = [
                os.path.join(mods_path, file)
                for file in os.listdir(mods_path)
                if file.endswith(".jar")
            ]  # jarファイルのパスを取得
            file_names = list(
                [os.path.basename(file_name) for file_name in file_paths]
            )  # 選択されたファイルの名前を取得
        except:
            # エラーになることはないが、念のためエラーメッセージを表示
            err_dlg(page, "エラー", "正式なファイルパスが渡されませんでした。")
            return

    else:
        # modsフォルダーのパスが存在しない場合、エラーメッセージを表示して関数を終了
        err_dlg(page, "エラー", "クリップボードにファイルパスがありません。")
        return

    if not file_paths == []:  # ファイルが選択された場合
        # それぞれのファイルを解凍→assets直下を
        main.process_app(file_paths, file_names, page)
    else:
        # file_pathsが空の場合、エラーメッセージを表示して関数を終了
        err_dlg(page, "エラー", "フォルダの中にjarファイルが存在しませんでした。")
        return


def start_gui(page: ft.Page):
    # ページの基本設定
    page.window_width = 1000
    page.window_height = 700
    page.theme = ft.Theme(
        color_scheme_seed="blue",
        font_family="Noto Sans JP",
    )
    page.padding = 30
    page.bgcolor = "#1a1c1e"
    page.update()

    pack_format = None

    # バージョンごとのpack_formatを辞書にしておく
    version_dict = {
        "1.13 ~ 1.14.4": 4,
        "1.15 ~ 1.16.1": 5,
        "1.16.2 ~ 1.16.5": 6,
        "1.17 ~ 1.17.1": 7,
        "1.18 ~ 1.18.2": 8,
        "1.19 ~ 1.19.2": 9,
        "1.19.3": 12,
        "1.19.4": 13,
        "1.20 ~ 1.20.1": 15,
        "1.20.2": 18,
        "1.20.3 ~ 1.20.4": 22,
        "1.20.5 ~ 1.20.6": 32,
    }

    # ドロップダウンの値が変更されたときに呼び出される関数
    def dropdown_changed(e):
        """ドロップダウンの値が変更されたときに呼び出される関数"""
        global pack_format
        pack_format = int(version_dict[dd.value])
        # アニメーションでボタンを表示
        button1.visible = True
        button2.visible = True
        button1.offset = ft.transform.Offset(0, 0)
        button2.offset = ft.transform.Offset(0, 0)
        page.update()

    def confirmOpenGitHub():
        def close_dlg(e):
            dlg.open = False
            page.update()

        def openGitHub(e):
            webbrowser.open("https://github.com/Maji3429/new-mc-mod-translating-tool")
            close_dlg(e)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("GitHub", size=20),
            content=ft.Container(
                content=ft.Text("GitHubのリンクを開きますか？"),
                padding=20,
            ),
            actions=[
                ft.TextButton("キャンセル", on_click=close_dlg),
                ft.TextButton(
                    "開く",
                    on_click=openGitHub,
                    style=ft.ButtonStyle(color="primary"),
                ),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # モダンなAppBarデザイン
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.G_TRANSLATE, color="#4a9eff", size=30),
        leading_width=40,
        title=ft.Text(
            "MC-MOD Translating tool",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#ffffff",
        ),
        center_title=True,
        bgcolor="#2b2e31",
        elevation=2,
        actions=[
            ft.IconButton(
                ft.icons.HELP_OUTLINE,
                icon_color="#4a9eff",
                tooltip="このアプリについて",
                on_click=lambda e: err_dlg(
                    page,
                    "このアプリについて",
                    "このアプリケーションは、MinecraftのMODを翻訳するためのツールです。一部翻訳できないMODがあります。",
                ),
            ),
            ft.IconButton(
                ft.icons.CODE_ROUNDED,
                icon_color="#4a9eff",
                tooltip="GitHubを開く",
                on_click=lambda e: confirmOpenGitHub(),
            ),
        ],
    )

    # スタイリッシュなドロップダウン
    dd = ft.Dropdown(
        on_change=dropdown_changed,
        label="MODの対応バージョン",
        width=300,
        border_color="#4a9eff",
        focused_border_color="#4a9eff",
        label_style=ft.TextStyle(color="#ffffff"),
        text_style=ft.TextStyle(color="#ffffff"),
        options=[ft.dropdown.Option(version) for version in version_dict.keys()],
    )

    pick_file_dialog = ft.FilePicker(
        on_result=lambda result: select_file(result, page)
    )
    page.overlay.append(pick_file_dialog)

    global selected_files
    selected_files = ft.Text(
        color="#ffffff",
        size=14,
    )

    # アニメーション付きのボタン
    button1 = ft.TextButton(
        text="翻訳するMODのjarファイルを選択",
        icon=ft.icons.ATTACH_FILE,
        style=ft.ButtonStyle(
            bgcolor="#2b2e31",
            color="#4a9eff",
        ),
        visible=False,
        offset=ft.transform.Offset(0, 0.5),  # 初期位置を下に
        animate_offset=ft.animation.Animation(300, "easeOut"),
        on_click=lambda e: pick_file_dialog.pick_files(
            allow_multiple=True,
            initial_directory=os.path.expanduser("~\\Downloads"),
            allowed_extensions=["jar"],
            dialog_title="翻訳するMODのjarファイルを選択(複数選択可)",
        ),
    )

    button2 = ft.TextButton(
        text="クリップボードからパスを取得",
        icon=ft.icons.CONTENT_PASTE,
        style=ft.ButtonStyle(
            bgcolor="#2b2e31",
            color="#4a9eff",
        ),
        visible=False,
        offset=ft.transform.Offset(0, 0.5),  # 初期位置を下に
        animate_offset=ft.animation.Animation(300, "easeOut"),
        on_click=lambda e: select_file_from_clipboard(page),
    )

    # メインコンテンツをカードで囲む
    main_content = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    dd,
                    ft.Divider(color="#4a9eff", height=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                        controls=[button1, button2],
                    ),
                    selected_files,
                ],
            ),
        ),
        elevation=5,
    )

    page.add(
        ft.Container(
            margin=ft.margin.only(top=20),
            content=main_content,
        )
    )


def make_progress_bar(page: ft.Page, lang_file_path):
    """
    翻訳ファイル名とプログレスバーを表示する関数。
    プログレスバーはカード内に横並びで表示され、複数ある場合はスクロール可能。

    Args:
        page (ft.Page): ページオブジェクト
        lang_file_path (str): 翻訳するファイルのパス

    Returns:
        tuple: (プログレスバー, 情報表示テキスト)
    """
    file_name = os.path.basename(os.path.dirname(os.path.dirname(lang_file_path)))
    
    # プログレスバーとテキスト
    pb = ft.ProgressBar(
        width=300,
        color="#4a9eff",
        bgcolor="#2b2e31",
    )
    
    show_info = ft.Text(
        "翻訳中...",
        color="#ffffff",
        size=14,
    )

    # 横並びレイアウト
    progress_row = ft.Row(
        controls=[
            # MOD名
            ft.Text(
                f"{file_name}",
                color="#ffffff",
                size=16,
                width=200,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.RIGHT,
            ),
            # 進捗状況
            ft.Column(
                controls=[
                    show_info,
                    pb,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # カードでラップ
    progress_card = ft.Card(
        content=ft.Container(
            content=progress_row,
            padding=15,
            border_radius=10,
        ),
        elevation=3,
    )

    # スクロール可能なコンテナがまだない場合は作成
    if not hasattr(page, 'progress_container'):
        page.progress_container = ft.Container(
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
            margin=ft.margin.only(top=20),
            height=200,  # スクロール可能な高さを設定
        )
        page.add(page.progress_container)

    # 新しいプログレスカードを追加
    page.progress_container.content.controls.append(progress_card)
    page.update()

    return pb, show_info


def progress_bar_update(
    pb: ft.ProgressBar, i: int, total_strings: int, show_info, page: ft.Page, start_time
):
    """
    プログレスバーを更新する関数
    Args:
        pb (ft.ProgressBar): プログレスバーオブジェクト
        i (int): 現在の翻訳された文字列の数
        total_strings (int): 総文字列数
        show_info (ft.Text): 翻訳中のファイル名を表示するテキストオブジェクト
        page (ft.Page): ページオブジェクト
    """
    pb.value = i / total_strings
    elapsed_time = time.time() - start_time
    avg_time_per_string = elapsed_time / i if i > 0 else 0
    remaining_strings = total_strings - i
    remaining_time = avg_time_per_string * remaining_strings
    show_info.value = f"翻訳中... 残り時間: {round(remaining_time)}秒"
    page.update()


def return_pack_format():
    """
    ドロップダウンで選択されたバージョンに対応するpack_formatを返す関数
    """
    return int(pack_format)


if __name__ == "__main__":
    ft.app(target=start_gui, assets_dir="assets")
