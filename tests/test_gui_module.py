import flet as ft
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui_module import start_gui


def test_start_gui_creates_appbar():
    page = ft.Page()
    start_gui(page)
    assert page.appbar is not None
    assert page.appbar.title.value == "MC-MOD Translating tool"


def test_start_gui_creates_dropdown():
    page = ft.Page()
    start_gui(page)
    dropdown = next(
        (control for control in page.controls if isinstance(control, ft.Dropdown)), None
    )
    assert dropdown is not None
    assert dropdown.label == "MODの対応バージョン"


def test_start_gui_creates_buttons():
    page = ft.Page()
    start_gui(page)
    button1 = next(
        (
            control
            for control in page.controls
            if isinstance(control, ft.TextButton)
            and control.text == "翻訳するMODのjarファイルを選択"
        ),
        None,
    )
    button2 = next(
        (
            control
            for control in page.controls
            if isinstance(control, ft.TextButton)
            and control.text == "クリップボードからパスを取得"
        ),
        None,
    )
    assert button1 is not None
    assert button2 is not None


def test_start_gui_buttons_initially_invisible():
    page = ft.Page()
    start_gui(page)
    button1 = next(
        (
            control
            for control in page.controls
            if isinstance(control, ft.TextButton)
            and control.text == "翻訳するMODのjarファイルを選択"
        ),
        None,
    )
    button2 = next(
        (
            control
            for control in page.controls
            if isinstance(control, ft.TextButton)
            and control.text == "クリップボードからパスを取得"
        ),
        None,
    )
    assert button1.visible == False
    assert button2.visible == False


def test_start_gui_dropdown_changes_button_visibility():
    page = ft.Page()
    start_gui(page)
    dropdown = next(
        (control for control in page.controls if isinstance(control, ft.Dropdown)), None
    )
    button1 = next(
        (
            control
            for control in page.controls
            if isinstance(control, ft.TextButton)
            and control.text == "翻訳するMODのjarファイルを選択"
        ),
        None,
    )
    button2 = next(
        (
            control
            for control in page.controls
            if isinstance(control, ft.TextButton)
            and control.text == "クリップボードからパスを取得"
        ),
        None,
    )
    dropdown.value = "1.13 ~ 1.14.4"
    dropdown.on_change(None)
    assert button1.visible == True
    assert button2.visible == True
