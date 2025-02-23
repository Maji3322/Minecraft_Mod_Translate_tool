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

# カラーパレットの定義
COLORS = {
    "primary": "#5B8FF9",  # メインカラー（より鮮やかな青）
    "background": "#1E1E2E",  # 背景色（より落ち着いた暗色）
    "card": "#2A2A3C",  # カード背景（より深みのある色）
    "text": "#FFFFFF",  # 文字色（白）
    "secondary": "#334656",  # セカンダリーカラー（ボタン背景など）
    "accent": "#6C7693",  # アクセントカラー
    "divider": "#5B8FF9",  # 区切り線
    "error": "#FF5555",  # エラー表示用
}

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
        logger.debug(f"Page state before update: {page}")
        page.update()
        logger.debug(f"Page state after update: {page}")

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
    ft.Text(file_paths, width=300, style=ft.TextStyle(bgcolor=COLORS["background"]))
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
    """
    GUIの初期設定を行う関数

    Args:
        page (ft.Page): ページオブジェクト

    Returns:
        None
    """
    # ページの基本設定
    page.window.width = 1000
    page.window.height = 700

    try:
        # 必要なモジュールを読み込む
        # Nuitkaビルド後、exeファイルからパスを導き出す
        if getattr(sys, "frozen", False):
            # コンパイルされた実行ファイルがあるパスを取得
            root_dir = os.path.dirname(sys.executable)
        else:
            # 通常のスクリプト実行時は__file__ベースでパスを取得
            root_dir = os.path.abspath(os.path.dirname(__file__))
        # アイコンファイルの絶対パスを作る
        icon_path = os.path.join(root_dir, "resources", "icon.ico")
        if os.path.exists(icon_path):
            page.window.icon = icon_path
            print(f"アイコンを設定しました: {icon_path}")
        else:
            print(f"警告: アイコンファイルが見つかりません: {icon_path}")
    except Exception as e:
        print(f"アイコン設定中にエラーが発生しました: {str(e)}")

    page.theme = ft.Theme(
        color_scheme_seed=COLORS["primary"],
        font_family="Noto Sans JP",
    )
    page.padding = 30
    page.bgcolor = COLORS["background"]
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
        "1.21 ~ 1.21.3": 35,
        "1.21.4": 46,
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
        leading=ft.Container(
            content=ft.Icon(ft.Icons.G_TRANSLATE, color=COLORS["primary"], size=30),
            padding=ft.padding.only(left=15),  # 左側に10ピクセルの余白を追加
        ),
        leading_width=40,
        title=ft.Text(
            "MC MOD Translator Tool",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=COLORS["text"],
        ),
        center_title=True,
        bgcolor=COLORS["card"],
        elevation=2,
        actions=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            ft.Icons.HELP_OUTLINE,
                            icon_color=COLORS["primary"],
                            tooltip="このアプリについて",
                            on_click=lambda e: err_dlg(
                                page,
                                "このアプリについて",
                                "このアプリケーションは、MinecraftのMODを翻訳するためのツールです。一部翻訳できないMODがあります。",
                            ),
                        ),
                        ft.IconButton(
                            ft.Icons.CODE_ROUNDED,
                            icon_color=COLORS["primary"],
                            tooltip="GitHubを開く",
                            on_click=lambda e: confirmOpenGitHub(),
                        ),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.only(right=10),  # 右側に20ピクセルの余白を追加
            ),
        ],
    )

    # スタイリッシュなドロップダウン
    dd = ft.Dropdown(
        on_change=dropdown_changed,
        label="MODの対応バージョン",
        width=300,
        border_color=COLORS["primary"],
        focused_border_color=COLORS["primary"],
        label_style=ft.TextStyle(color=COLORS["text"]),
        text_style=ft.TextStyle(color=COLORS["text"]),
        options=[ft.dropdown.Option(version) for version in version_dict.keys()],
    )

    pick_file_dialog = ft.FilePicker(on_result=lambda result: select_file(result, page))
    page.overlay.append(pick_file_dialog)

    global selected_files
    selected_files = ft.Text(
        color=COLORS["text"],
        size=14,
    )

    # アニメーション付きのボタン
    button1 = ft.TextButton(
        text="翻訳するMODのjarファイルを選択",
        icon=ft.Icons.ATTACH_FILE,
        style=ft.ButtonStyle(
            bgcolor=COLORS["secondary"],
            color=COLORS["text"],
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
        icon=ft.Icons.CONTENT_PASTE,
        style=ft.ButtonStyle(
            bgcolor=COLORS["secondary"],
            color=COLORS["text"],
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
                    ft.Divider(color=COLORS["divider"], height=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                        controls=[button1, button2],
                    ),
                    selected_files,
                ],
            ),
        ),
        elevation=8,
        color=COLORS["card"],
    )

    page.add(
        ft.Container(
            margin=ft.margin.only(top=20),
            content=main_content,
        )
    )

    def page_resize(e):
        """ウィンドウサイズ変更時にスクロール枠のサイズを更新"""
        if hasattr(page, "progress_container"):
            # スクロールコンテナの高さを更新
            page.progress_container.height = page.window_height - 150
            page.update()

    # ウィンドウサイズ変更イベントのハンドラを設定
    page.on_resize = page_resize


def hide_selection_ui(page: ft.Page):
    """
    バージョン選択やファイル選択のUI要素を非表示にする関数

    Args:
        page (ft.Page): ページオブジェクト
    """
    # メインコンテンツを取得（最初のCard）
    main_card = None
    for control in page.controls:
        if isinstance(control, ft.Container) and isinstance(control.content, ft.Card):
            main_card = control
            break

    if main_card:
        # メインカードを非表示
        main_card.visible = False
        page.update()


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
    # ローディングインジケータが表示されている場合は非表示にする
    hide_loading(page)

    file_name = os.path.basename(os.path.dirname(os.path.dirname(lang_file_path)))

    # プログレスバーとテキスト
    pb = ft.ProgressBar(
        width=300,
        color=COLORS["primary"],
        bgcolor=COLORS["card"],
    )

    show_info = ft.Text(
        "翻訳中...",
        color=COLORS["text"],
        size=14,
    )

    # カード内の2カラムレイアウト
    progress_columns = ft.Row(
        controls=[
            # 左カラム (MOD名)
            ft.Container(
                content=ft.Text(
                    f"{file_name}",
                    color=COLORS["text"],
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                alignment=ft.alignment.center,
                expand=True,  # カラムを均等に広げる
            ),
            # 区切り線
            ft.VerticalDivider(
                width=1,
                color=COLORS["divider"],
            ),
            # 右カラム (進捗状況)
            ft.Container(
                content=ft.Column(
                    controls=[
                        show_info,
                        pb,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                expand=True,  # カラムを均等に広げる
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # カードでラップ
    progress_card = ft.Card(
        content=ft.Container(
            content=progress_columns,
            padding=15,
            border_radius=10,
        ),
        elevation=8,
        color=COLORS["card"],
    )

    # スクロール可能なコンテナがまだない場合は作成
    if not hasattr(page, "progress_container"):
        page.progress_container = ft.Container(
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                # 下部に余白を追加してスクロール時も見やすく
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(top=20, bottom=20),
            # ウィンドウの高さからAppBarとマージンを引いた高さに設定
            height=page.window_height - 150,  # AppBarの高さ(64px)+ 上下マージン(86px)
            expand=True,  # コンテナを利用可能なスペースいっぱいに広げる
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
    try:
        logger.info("Updating progress bar")
        pb.value = i / total_strings
        elapsed_time = time.time() - start_time
        avg_time_per_string = elapsed_time / i if i > 0 else 0
        remaining_strings = total_strings - i
        remaining_time = avg_time_per_string * remaining_strings
        show_info.value = f"翻訳中... 残り時間: {round(remaining_time)}秒"
        logger.debug("Page state before update: %s", page)
        page.update()
        logger.debug("Page state after update: %s", page)
        logger.info("Progress bar updated successfully")
    except Exception as e:
        logger.error("Error updating progress bar: %s", e, exc_info=True)
        logger.error(
            f"logger info:\npb.value={pb.value}\ni={i}\ntotal_strings={total_strings}\nshow_info.value={show_info.value}"
        )
        raise


def return_pack_format():
    """
    ドロップダウンで選択されたバージョンに対応するpack_formatを返す関数
    """
    return int(pack_format)


def make_extract_progress(page: ft.Page):
    """
    jarファイルの解凍進捗を表示するUIを作成する関数。

    Args:
        page (ft.Page): ページオブジェクト

    Returns:
        tuple: (プログレスバー, 情報表示テキスト)
    """
    # プログレスバーとテキスト
    pb = ft.ProgressBar(
        width=300,
        color=COLORS["primary"],
        bgcolor=COLORS["card"],
    )

    show_info = ft.Text(
        "解凍中...",
        color=COLORS["text"],
        size=14,
    )

    # 進捗表示レイアウト
    progress_row = ft.Row(
        controls=[
            # 解凍中の表示とファイル名を横並びに
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            "解凍中：",
                            color=COLORS["text"],
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        ),
                        show_info,
                    ],
                    width=400,  # 固定幅を設定
                ),
                alignment=ft.alignment.center,  # 中央寄せ
            ),
            # 進捗バー
            pb,
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # 全体を中央寄せ
        spacing=20,
    )

    # カードでラップ
    progress_card = ft.Card(
        content=ft.Container(
            content=progress_row,
            padding=15,
            border_radius=10,
            alignment=ft.alignment.center,  # コンテナ内も中央寄せ
        ),
        elevation=8,
        color=COLORS["card"],
    )

    # スクロール可能なコンテナを作成・更新
    if not hasattr(page, "progress_container"):
        page.progress_container = ft.Container(
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                # 下部に余白を追加してスクロール時も見やすく
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(top=20, bottom=20),
            # ウィンドウの高さからAppBarとマージンを引いた高さに設定
            height=page.window_height - 150,  # AppBarの高さ(64px)+ 上下マージン(86px)
            expand=True,  # コンテナを利用可能なスペースいっぱいに広げる
        )
        page.add(page.progress_container)

    page.progress_container.content.controls.append(progress_card)
    page.update()

    return pb, show_info


def update_extract_progress(
    pb: ft.ProgressBar,
    current: int,
    total: int,
    show_info,
    page: ft.Page,
    file_name: str,
):
    """
    解凍進捗バーを更新する関数

    Args:
        pb (ft.ProgressBar): プログレスバーオブジェクト
        current (int): 現在の処理ファイル番号
        total (int): 総ファイル数
        show_info (ft.Text): 情報表示テキストオブジェクト

        page (ft.Page): ページオブジェクト
        file_name (str): 現在処理中のファイル名
    """
    pb.value = current / total
    # ファイル名が30文字を超える場合は省略
    if len(file_name) > 30:
        truncated_name = file_name[:27] + "..."
    else:
        truncated_name = file_name
    show_info.value = f"{truncated_name} ({current}/{total})"
    page.update()


def hide_extract_progress(page: ft.Page):
    """
    解凍進捗のプログレスバーを非表示にする関数

    Args:
        page (ft.Page): ページオブジェクト
    """
    if hasattr(page, "progress_container") and page.progress_container.content.controls:
        # 最初のプログレスカード（解凍進捗）を非表示
        extract_card = page.progress_container.content.controls[0]
        page.progress_container.content.controls.remove(extract_card)

        # ローディングインジケータを表示
        show_loading(page)
        page.update()


def show_loading(page: ft.Page):
    """
    翻訳準備中のローディングインジケータを表示する関数

    Args:
        page (ft.Page): ページオブジェクト
    """
    loading_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(
                    width=40,
                    height=40,
                    stroke_width=3,
                    color=COLORS["primary"],
                ),
                ft.Text(
                    "翻訳の準備中...",
                    color=COLORS["text"],
                    size=14,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        alignment=ft.alignment.center,
    )

    if not hasattr(page, "progress_container"):
        page.progress_container = ft.Container(
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(top=20, bottom=20),
            height=page.window_height - 150,
            expand=True,
        )
        page.add(page.progress_container)

    page.progress_container.content.controls.append(loading_container)
    page.loading_container = loading_container
    page.update()


def hide_loading(page: ft.Page):
    """
    ローディングインジケータを非表示にする関数

    Args:
        page (ft.Page): ページオブジェクト
    """
    if hasattr(page, "loading_container"):
        page.progress_container.content.controls.remove(page.loading_container)
        delattr(page, "loading_container")
        page.update()
