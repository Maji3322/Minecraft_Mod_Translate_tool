"""Reusable UI components for the application."""

import logging
import os
import time
import webbrowser
from typing import Callable, List, Optional, Tuple

import flet as ft
import pyperclip

from ..utils.config import config
from ..utils.exceptions import UIError

logger = logging.getLogger(__name__)

# Keys for storing UI components in page data
PROGRESS_CONTAINER_KEY = "progress_container"
LOADING_CONTAINER_KEY = "loading_container"

# UI text constants
TEXT_EXTRACTION_CARD = "MODファイルの解凍"
TEXT_TRANSLATING = "翻訳中..."
TEXT_PROCESSING = "処理中..."
TEXT_CLOSE = "閉じる"
TEXT_CANCEL = "キャンセル"
TEXT_OPEN = "開く"
TEXT_GITHUB_CONFIRM = "GitHubのリンクを開きますか？"
TEXT_GITHUB_TITLE = "GitHub"

# GitHub repository URL
GITHUB_REPO_URL = "https://github.com/Maji3429/new-mc-mod-translating-tool"

# UI sizing constants
DEFAULT_WINDOW_HEIGHT = 500
WINDOW_HEIGHT_OFFSET = 150
PROGRESS_BAR_WIDTH = 300
LOADING_RING_SIZE = 50
LOADING_RING_STROKE = 4


def initialize_page_data(page: ft.Page) -> None:
    """Ensure that the page has a data attribute initialized as a dictionary.

    Args:
        page: The page to initialize data for.
    """
    if not hasattr(page, "data") or page.data is None:
        page.data = {}


def show_dialog(
    page: ft.Page,
    title: str,
    content: str,
    actions: Optional[List[ft.Control]] = None,
    on_dismiss: Optional[Callable] = None,
    modal: bool = True,
) -> None:
    """Show a dialog with the given title and content.

    Args:
        page: The page to show the dialog on.
        title: Dialog title.
        content: Dialog content.
        actions: Dialog actions.
        on_dismiss: Callback when dialog is dismissed.
        modal: Whether the dialog is modal.
    """

    def close_dialog(e):
        page.pop_dialog()
        if on_dismiss:
            on_dismiss()

    if actions is None:
        actions = [ft.TextButton(TEXT_CLOSE, on_click=close_dialog)]

    dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(content) if isinstance(content, str) else content,
        actions=actions,
        actions_alignment=ft.MainAxisAlignment.END,
        modal=modal,
    )

    page.show_dialog(dialog)


def show_error_dialog(page: ft.Page, title: str, message: str) -> None:
    """Show an error dialog.

    Args:
        page: The page to show the dialog on.
        title: Dialog title.
        message: Error message.
    """
    show_dialog(page, title, message)


def show_github_dialog(page: ft.Page) -> None:
    """Show a dialog to confirm opening GitHub.

    Args:
        page: The page to show the dialog on.
    """

    def open_github(e):
        webbrowser.open(GITHUB_REPO_URL)
        close_dialog(e)

    def close_dialog(e):
        page.pop_dialog()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(TEXT_GITHUB_TITLE, size=20),
        content=ft.Container(
            content=ft.Text(TEXT_GITHUB_CONFIRM),
            padding=20,
        ),
        actions=[
            ft.TextButton(TEXT_CANCEL, on_click=close_dialog),
            ft.TextButton(
                TEXT_OPEN,
                on_click=open_github,
                style=ft.ButtonStyle(color=config.COLORS["primary"]),
            ),
        ],
    )

    page.show_dialog(dialog)


def make_loading_indicator(page: ft.Page) -> ft.Container:
    """Create a loading indicator.

    Args:
        page: The page to add the loading indicator to.

    Returns:
        The loading indicator container.
    """
    loading_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(
                    width=LOADING_RING_SIZE,
                    height=LOADING_RING_SIZE,
                    stroke_width=LOADING_RING_STROKE,
                    color=config.COLORS["primary"],
                ),
                ft.Text(
                    TEXT_PROCESSING,
                    color=config.COLORS["text"],
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        visible=False,
    )

    initialize_page_data(page)
    page.data[LOADING_CONTAINER_KEY] = loading_container
    page.add(loading_container)

    return loading_container


def show_loading(page: ft.Page) -> None:
    """Show the loading indicator.

    Args:
        page: The page containing the loading indicator.
    """
    initialize_page_data(page)

    loading_container = page.data.get(LOADING_CONTAINER_KEY)

    if loading_container and isinstance(loading_container, ft.Container):
        loading_container.visible = True
        page.update()
    else:
        logger.warning("Loading container not found in page data.")


def hide_loading(page: ft.Page) -> None:
    """Hide the loading indicator.

    Args:
        page: The page containing the loading indicator.
    """
    initialize_page_data(page)

    loading_container = page.data.get(LOADING_CONTAINER_KEY)

    if loading_container and isinstance(loading_container, ft.Container):
        loading_container.visible = False
        page.update()
    else:
        logger.warning("Loading container not found in page data.")


def make_progress_bar(page: ft.Page, file_path: str) -> Tuple[ft.ProgressBar, ft.Text]:
    """Create a progress bar for translation.

    Args:
        page: The page to add the progress bar to.
        file_path: The path of the file being translated.

    Returns:
        A tuple containing the progress bar and info text.
    """
    hide_loading(page)

    file_name = os.path.basename(os.path.dirname(os.path.dirname(file_path)))

    progress_bar = ft.ProgressBar(
        width=PROGRESS_BAR_WIDTH,
        color=config.COLORS["primary"],
        bgcolor=config.COLORS["card"],
    )

    info_text = ft.Text(
        TEXT_TRANSLATING,
        color=config.COLORS["text"],
        size=14,
    )

    progress_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            f"{file_name}",
                            color=config.COLORS["text"],
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    ),
                    ft.VerticalDivider(
                        width=1,
                        color=config.COLORS["divider"],
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                info_text,
                                progress_bar,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ),
        elevation=4,
        bgcolor=config.COLORS["card"],
    )

    initialize_page_data(page)

    progress_container = page.data.get(PROGRESS_CONTAINER_KEY)

    if not progress_container:
        window_height = (
            page.window.height - WINDOW_HEIGHT_OFFSET
            if page.window and page.window.height
            else DEFAULT_WINDOW_HEIGHT
        )

        progress_container = ft.Container(
            content=ft.Column(
                controls=[progress_card],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            height=window_height,
            visible=True,
        )

        page.data[PROGRESS_CONTAINER_KEY] = progress_container
        page.add(progress_container)
    else:
        if isinstance(progress_container, ft.Container) and isinstance(
            progress_container.content, ft.Column
        ):
            _remove_extraction_card(progress_container)
            progress_container.content.controls.append(progress_card)
            progress_container.visible = True
            page.update()

    return progress_bar, info_text


def update_progress_bar(
    progress_bar: ft.ProgressBar,
    current: int,
    total: int,
    info_text: ft.Text,
    page: ft.Page,
    start_time: float,
) -> None:
    """
    Update a progress bar.

    Args:
        progress_bar: The progress bar to update
        current: Current progress
        total: Total progress
        info_text: Info text to update
        page: The page containing the progress bar
        start_time: Time when the operation started
    """
    # Calculate progress
    progress = current / total if total > 0 else 0
    progress_bar.value = progress

    # Calculate elapsed time and estimated time remaining
    elapsed_time = time.time() - start_time
    if current > 0:
        estimated_total_time = elapsed_time * total / current
        remaining_time = estimated_total_time - elapsed_time

        # Format time strings
        elapsed_str = format_time(elapsed_time)
        remaining_str = format_time(remaining_time)

        info_text.value = f"翻訳中... {current}/{total} ({progress:.1%}) - 経過時間: {elapsed_str}, 残り時間: {remaining_str}"
    else:
        info_text.value = f"翻訳中... {current}/{total} ({progress:.1%})"

    # Update the page
    page.update()


def format_time(seconds: float) -> str:
    """
    Format time in seconds to a human-readable string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}時間"


def hide_progress_bars(page: ft.Page) -> None:
    """
    Hide all progress bars.

    Args:
        page: The page containing the progress bars
    """
    if not hasattr(page, "data") or page.data is None:
        page.data = {}

    progress_container = page.data.get(PROGRESS_CONTAINER_KEY)

    if progress_container and isinstance(progress_container, ft.Container):
        progress_container.visible = False
        page.update()
    else:
        logger.warning("Progress container not found in page data.")


def make_extract_progress(page: ft.Page) -> Tuple[ft.ProgressBar, ft.Text]:
    """
    Create a progress bar for extraction.

    Args:
        page: The page to add the progress bar to

    Returns:
        A tuple containing the progress bar and info text
    """
    # Create progress bar and info text
    progress_bar = ft.ProgressBar(
        width=300,
        color=config.COLORS["primary"],
        bgcolor=config.COLORS["card"],
    )

    info_text = ft.Text(
        "解凍中...",
        color=config.COLORS["text"],
        size=14,
    )

    # Create a card with the progress bar
    extract_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(
                        TEXT_EXTRACTION_CARD,
                        color=config.COLORS["text"],
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    info_text,
                    progress_bar,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
        ),
        elevation=4,
        bgcolor=config.COLORS["card"],
    )

    # Create or get the progress container
    if not hasattr(page, "data") or page.data is None:
        page.data = {}

    progress_container = page.data.get(PROGRESS_CONTAINER_KEY)

    if not progress_container:
        # Create a new container for progress cards
        progress_container = ft.Container(
            content=ft.Column(
                controls=[extract_card],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            height=(
                page.window.height - 150 if page.window and page.window.height else 500
            ),
            visible=True,
        )

        # Store the container in page data
        page.data[PROGRESS_CONTAINER_KEY] = progress_container
        page.add(progress_container)
    else:
        # Add the extract card to the existing container
        if isinstance(progress_container, ft.Container) and isinstance(
            progress_container.content, ft.Column
        ):
            progress_container.content.controls = [
                extract_card
            ]  # Replace existing controls
            progress_container.visible = True
            page.update()

    return progress_bar, info_text


def update_extract_progress(
    progress_bar: ft.ProgressBar,
    current: int,
    total: int,
    info_text: ft.Text,
    page: ft.Page,
    file_name: str,
) -> None:
    """
    Update the extraction progress bar.

    Args:
        progress_bar: The progress bar to update
        current: Current progress
        total: Total progress
        info_text: Info text to update
        page: The page containing the progress bar
        file_name: Name of the file being extracted
    """
    # Calculate progress
    progress = current / total if total > 0 else 0
    progress_bar.value = progress

    # Update info text
    info_text.value = f"解凍中... {current}/{total} ({progress:.1%}) - {file_name}"

    # Update the page
    page.update()


def _remove_extraction_card(progress_container: ft.Container) -> bool:
    """
    Remove the extraction card from the progress container.

    Args:
        progress_container: The progress container

    Returns:
        True if the extraction card was found and removed, False otherwise
    """
    if not isinstance(progress_container, ft.Container) or not isinstance(
        progress_container.content, ft.Column
    ):
        return False

    for i, control in enumerate(progress_container.content.controls):
        if isinstance(control, ft.Card) and isinstance(control.content, ft.Container):
            container_content = control.content.content
            if isinstance(container_content, ft.Column):
                for sub_control in container_content.controls:
                    if (
                        isinstance(sub_control, ft.Text)
                        and sub_control.value == TEXT_EXTRACTION_CARD
                    ):
                        progress_container.content.controls.pop(i)
                        return True

    return False


def hide_extract_progress(page: ft.Page) -> None:
    """
    Hide the extraction progress bar and remove it from the container.

    Args:
        page: The page containing the extraction progress bar
    """
    if not hasattr(page, "data") or page.data is None:
        page.data = {}

    progress_container = page.data.get(PROGRESS_CONTAINER_KEY)

    if progress_container:
        # Remove the extraction card
        removed = _remove_extraction_card(progress_container)

        # Hide the container if it's now empty
        if removed and not progress_container.content.controls:
            progress_container.visible = False

        page.update()
    else:
        logger.warning("Progress container not found in page data.")
        # Fall back to the original behavior
        hide_progress_bars(page)


def hide_selection_ui(page: ft.Page) -> None:
    """
    Hide the version selection and file selection UI.

    Args:
        page: The page containing the selection UI
    """
    # Find the main card container
    main_card_container = None

    if page.controls:
        for control in page.controls:
            if isinstance(control, ft.Container) and isinstance(
                control.content, ft.Card
            ):
                main_card_container = control
                break

    if main_card_container:
        main_card_container.visible = False
        page.update()
    else:
        logger.warning("Main card container not found.")


def select_file_from_clipboard(page: ft.Page, process_callback: Callable) -> None:
    """
    Select files from the clipboard path.

    Args:
        page: The page
        process_callback: Callback to process the selected files
    """
    try:
        # Get the path from clipboard
        mods_path = pyperclip.paste().replace('"', "")

        # Check if the path exists
        if not os.path.exists(mods_path):
            show_error_dialog(
                page, "エラー", "クリップボードにファイルパスがありません。"
            )
            return

        # Get all JAR files in the directory
        file_paths = [
            os.path.join(mods_path, file)
            for file in os.listdir(mods_path)
            if file.endswith(".jar")
        ]

        if not file_paths:
            show_error_dialog(
                page, "エラー", "フォルダの中にjarファイルが存在しませんでした。"
            )
            return

        # Get file names
        file_names = [os.path.basename(file_path) for file_path in file_paths]

        # Process the files
        process_callback(file_paths, file_names, page)

    except Exception as e:
        logger.error(f"Error selecting files from clipboard: {e}", exc_info=True)
        show_error_dialog(
            page, "エラー", f"ファイル選択中にエラーが発生しました: {str(e)}"
        )
        raise UIError("Failed to select files from clipboard") from e


def show_openrouter_settings_dialog(page: ft.Page, on_save: Callable) -> None:
    """
    Show a dialog for OpenRouter API key and model configuration.

    Args:
        page: The page to show the dialog on
        on_save: Callback function when settings are saved
    """
    from ..core.openrouter_api import OpenRouterAPI

    # Create API key input field
    api_key_field = ft.TextField(
        label="OpenRouter APIキー",
        password=True,
        can_reveal_password=True,
        hint_text="sk-or-v1-...",
        value=config.OPENROUTER_API_KEY if config.OPENROUTER_API_KEY else "",
        width=500,
    )

    # Create model search field
    model_search_field = ft.TextField(
        label="モデル検索 (部分一致)",
        hint_text="llama, gpt, gemini など",
        width=500,
    )

    # Create model list view
    model_listview = ft.ListView(
        height=300,
        width=500,
        spacing=5,
    )

    # Create fallback models list
    fallback_models_column = ft.Column(
        spacing=5,
        scroll=ft.ScrollMode.AUTO,
        height=150,
    )

    # Selected primary model
    selected_model = {
        "value": config.OPENROUTER_MODEL if config.OPENROUTER_MODEL else ""
    }

    # Available models cache
    available_models = {"data": []}

    # Loading indicator
    loading_text = ft.Text("", color=config.COLORS["text"], size=12)

    # Initialize fallback models from config
    def initialize_fallback_models():
        """Initialize fallback models from configuration."""
        if hasattr(config, "FALLBACK_MODELS") and config.FALLBACK_MODELS:
            for model_name in config.FALLBACK_MODELS:
                if not model_name:
                    continue
                delete_btn = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_size=16,
                )
                fallback_tile = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(model_name, size=12, expand=True),
                            delete_btn,
                        ]
                    ),
                    data=model_name,
                    bgcolor=config.COLORS["secondary"],
                    padding=5,
                    border_radius=5,
                )
                delete_btn.on_click = lambda _, c=fallback_tile: remove_fallback(c)
                fallback_models_column.controls.append(fallback_tile)

    def fetch_models_async():
        """Fetch models from OpenRouter API."""
        try:
            loading_text.value = "モデルを取得中..."
            page.update()

            api_key = api_key_field.value.strip() if api_key_field.value else ""
            api = OpenRouterAPI(api_key if api_key else None)
            models = api.fetch_models()
            available_models["data"] = models

            loading_text.value = f"{len(models)}個のモデルが利用可能"
            update_model_list("")
            page.update()

        except Exception as e:
            loading_text.value = f"エラー: {str(e)}"
            logger.error(f"Failed to fetch models: {e}")
            page.update()

    def update_model_list(search_term: str):
        """Update the model list based on search term."""
        model_listview.controls.clear()

        if not available_models["data"]:
            model_listview.controls.append(
                ft.Text("モデルを取得してください", color=config.COLORS["text"])
            )
            page.update()
            return

        api = OpenRouterAPI()
        filtered_models = api.search_models(available_models["data"], search_term)

        if not filtered_models:
            model_listview.controls.append(
                ft.Text("検索結果なし", color=config.COLORS["text"])
            )
            page.update()
            return

        for model in filtered_models[:50]:  # Limit to 50 results
            model_id = model.get("id", "")
            model_name = model.get("name", "Unknown")
            pricing = model.get("pricing", {})
            is_free = (
                str(pricing.get("prompt", "0")) == "0"
                and str(pricing.get("completion", "0")) == "0"
            )

            # Create model tile
            tile = ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(model_name, weight=ft.FontWeight.BOLD, size=14),
                                ft.Text(
                                    model_id, size=11, color=config.COLORS["accent"]
                                ),
                                ft.Text(
                                    "無料" if is_free else "有料",
                                    size=10,
                                    color=(
                                        config.COLORS["primary"]
                                        if is_free
                                        else config.COLORS["error"]
                                    ),
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=(
                                ft.Icons.CHECK_CIRCLE
                                if model_id == selected_model["value"]
                                else ft.Icons.CIRCLE_OUTLINED
                            ),
                            icon_color=(
                                config.COLORS["primary"]
                                if model_id == selected_model["value"]
                                else config.COLORS["accent"]
                            ),
                            on_click=lambda e, mid=model_id: select_model(mid),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=config.COLORS["card"],
                padding=10,
                border_radius=5,
            )
            model_listview.controls.append(tile)

        page.update()

    def select_model(model_id: str):
        """Select a model as primary."""
        selected_model["value"] = model_id
        update_model_list(model_search_field.value or "")

    def on_search_change(e):
        """Handle search field change."""
        update_model_list(e.control.value or "")

    def add_fallback_model():
        """Add currently selected model to fallback list."""
        if selected_model["value"] and selected_model["value"] not in [
            c.data for c in fallback_models_column.controls
        ]:
            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_size=16,
            )
            fallback_tile = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(selected_model["value"], size=12, expand=True),
                        delete_btn,
                    ]
                ),
                data=selected_model["value"],
                bgcolor=config.COLORS["secondary"],
                padding=5,
                border_radius=5,
            )
            delete_btn.on_click = lambda _, c=fallback_tile: remove_fallback(c)
            fallback_models_column.controls.append(fallback_tile)
            page.update()

    def remove_fallback(container):
        """Remove a fallback model."""
        if container in fallback_models_column.controls:
            fallback_models_column.controls.remove(container)
            page.update()

    def save_settings(e):
        """Save settings and close dialog."""
        # Save API key (in memory only)
        api_key = api_key_field.value.strip() if api_key_field.value else ""
        if not api_key:
            show_error_dialog(page, "エラー", "APIキーを入力してください")
            return

        if not selected_model["value"]:
            show_error_dialog(page, "エラー", "モデルを選択してください")
            return

        # Check if API key changed
        api_key_changed = config.OPENROUTER_API_KEY != api_key

        config.OPENROUTER_API_KEY = api_key
        config.OPENROUTER_MODEL = selected_model["value"]

        # Save fallback models
        fallback_list = [c.data for c in fallback_models_column.controls]
        config.FALLBACK_MODELS = fallback_list

        # Reset client cache if API key changed
        if api_key_changed:
            from ..core.translator import reset_openrouter_client

            reset_openrouter_client()

        page.pop_dialog()

        # Call callback
        on_save()

    def close_dialog(e):
        """Close the dialog."""
        page.pop_dialog()

    # Connect event handlers
    model_search_field.on_change = on_search_change

    # Create dialog content
    content = ft.Column(
        [
            api_key_field,
            ft.Row(
                [
                    ft.ElevatedButton(
                        "モデルを取得",
                        on_click=lambda e: fetch_models_async(),
                        icon=ft.Icons.DOWNLOAD,
                    ),
                    loading_text,
                ],
                spacing=10,
            ),
            ft.Divider(),
            model_search_field,
            ft.Text("利用可能なモデル:", weight=ft.FontWeight.BOLD),
            model_listview,
            ft.Divider(),
            ft.Row(
                [
                    ft.Text("フォールバックモデル:", weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        on_click=lambda e: add_fallback_model(),
                        tooltip="選択中のモデルをフォールバックに追加",
                    ),
                ],
            ),
            fallback_models_column,
            ft.Text(
                "※ フォールバックモデルはレート制限時に順番に試行されます",
                size=10,
                color=config.COLORS["accent"],
            ),
        ],
        width=550,
        scroll=ft.ScrollMode.AUTO,
    )

    # Create dialog
    dialog = ft.AlertDialog(
        title=ft.Text("OpenRouter設定"),
        content=content,
        actions=[
            ft.TextButton("キャンセル", on_click=close_dialog),
            ft.ElevatedButton("保存", on_click=save_settings),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        modal=True,
    )

    # Initialize fallback models from config
    initialize_fallback_models()

    # Show dialog
    page.show_dialog(dialog)
