"""UI styles and themes for the application."""

import flet as ft
from platform import system

from ..utils.config import config

COLORS = config.COLORS

def get_system_font() -> str:
    """
    Get the system font based on the operating system.

    Returns:
        The system font name
    """
    os_name = system()
    if os_name == "Windows":
        return "Noto Sans JP"
    elif os_name == "Darwin":  # macOS
        return "Hiragino Sans"
    else:  # Linux and others
        return "Noto Sans CJK JP"

def create_theme() -> ft.Theme:
    """Create the application theme.

    Returns:
        The application theme.
    """
    return ft.Theme(
        color_scheme_seed=COLORS["primary"],
        font_family=get_system_font(),
    )


def create_app_bar(
    page: ft.Page, on_help_click=None, on_github_click=None, on_settings_click=None
) -> ft.AppBar:
    """Create the application bar.

    Args:
        page: The page to add the app bar to.
        on_help_click: Callback for help button click.
        on_github_click: Callback for GitHub button click.
        on_settings_click: Callback for settings button click.

    Returns:
        The application bar.
    """
    return ft.AppBar(
        leading=ft.Container(
            content=ft.Icon(ft.Icons.G_TRANSLATE, color=COLORS["primary"], size=30),
            padding=ft.padding.only(left=15),
        ),
        leading_width=40,
        title=ft.Text(
            f"MC MOD Translator Tool v{config.get_app_version()}",
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
                            ft.Icons.SETTINGS,
                            icon_color=COLORS["primary"],
                            tooltip="OpenRouter設定",
                            on_click=on_settings_click,
                        ),
                        ft.IconButton(
                            ft.Icons.HELP_OUTLINE,
                            icon_color=COLORS["primary"],
                            tooltip="このアプリについて",
                            on_click=on_help_click,
                        ),
                        ft.IconButton(
                            ft.Icons.CODE_ROUNDED,
                            icon_color=COLORS["primary"],
                            tooltip="GitHubを開く",
                            on_click=on_github_click,
                        ),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.only(right=10),
            ),
        ],
    )


def create_button(
    text: str, icon: str, on_click=None, visible: bool = True, animate: bool = True
) -> ft.TextButton:
    """Create a styled button.

    Args:
        text: Button text.
        icon: Button icon.
        on_click: Click event handler.
        visible: Whether the button is visible.
        animate: Whether to animate the button.

    Returns:
        The styled button.
    """
    button = ft.TextButton(
        text=text,
        icon=icon,
        style=ft.ButtonStyle(
            bgcolor=COLORS["secondary"],
            color=COLORS["text"],
        ),
        visible=visible,
        on_click=on_click,
    )

    if animate:
        button.offset = ft.Offset(0, 0.5)
        button.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)

    return button


def create_dropdown(
    label: str, options: list, width: int = 300, on_change=None
) -> ft.Dropdown:
    """Create a styled dropdown.

    Args:
        label: Dropdown label.
        options: Dropdown options.
        width: Dropdown width.
        on_change: Change event handler.

    Returns:
        The styled dropdown.
    """
    return ft.Dropdown(
        label=label,
        options=[ft.dropdown.Option(option) for option in options],
        width=width,
        border_color=COLORS["primary"],
        focused_border_color=COLORS["primary"],
        label_style=ft.TextStyle(color=COLORS["text"]),
        text_style=ft.TextStyle(color=COLORS["text"]),
        on_change=on_change,
    )


def create_card(content: ft.Control) -> ft.Card:
    """Create a styled card.

    Args:
        content: Card content.

    Returns:
        The styled card.
    """
    return ft.Card(
        content=ft.Container(
            padding=20,
            content=content,
        ),
        elevation=8,
        color=COLORS["card"],
    )
