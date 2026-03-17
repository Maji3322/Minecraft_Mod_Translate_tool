"""Main UI application for the Minecraft MOD Translator Tool."""

import asyncio
import glob
import logging
import os
import sys
import threading
import time
from typing import List

import flet as ft
from plyer import notification

from ..core import file_manager, resource_pack, translator
from ..utils.config import config
from ..utils.exceptions import (
    FileOperationError,
    ResourcePackError,
    TranslationError,
    UIError,
)
from . import components, styles

logger = logging.getLogger(__name__)

# Window sizing constants
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700
DEFAULT_WINDOW_PADDING = 30

# UI text constants
TEXT_FILE_BUTTON = "翻訳するMODのjarファイルを選択"
TEXT_CLIPBOARD_BUTTON = "クリップボードからパスを取得"
TEXT_TRANSLATE_BUTTON = "翻訳開始"
TEXT_FILE_PICKER_TITLE = "翻訳するMODのjarファイルを選択(複数選択可)"
TEXT_NOTIFICATION_TITLE = "翻訳完了"
TEXT_NOTIFICATION_SUCCESS = "翻訳が完了しました！リソースパックを確認してください。"
TEXT_ABOUT_DIALOG = (
    "このアプリケーションは、MinecraftのMODを翻訳するためのツールです。"
    "一部翻訳できないMODがあります。"
)

# Notification settings
NOTIFICATION_TIMEOUT = 10


class MinecraftModTranslatorApp:
    """Main application class for the Minecraft MOD Translator Tool."""

    def __init__(self):
        """Initialize the application."""
        self.selected_files_text = ft.Text("", color=config.COLORS["text"], size=14)
        self.file_names: List[str] = []
        self._loop: asyncio.AbstractEventLoop | None = None
        self._status_dot: ft.Container | None = None
        self._status_text: ft.Text | None = None

    def initialize_ui(self, page: ft.Page) -> None:
        """Initialize the UI.

        Args:
            page: The page to initialize.
        """
        self._loop = asyncio.get_running_loop()
        page.window.width = DEFAULT_WINDOW_WIDTH
        page.window.height = DEFAULT_WINDOW_HEIGHT
        page.theme = styles.create_theme()
        page.padding = DEFAULT_WINDOW_PADDING
        page.bgcolor = config.COLORS["background"]

        self._set_window_icon(page)

        # Create Ollama status indicator
        status_container, self._status_dot, self._status_text = (
            components.create_ollama_status_indicator()
        )

        page.appbar = styles.create_app_bar(
            page,
            on_help_click=lambda e: components.show_dialog(
                page, "このアプリについて", TEXT_ABOUT_DIALOG
            ),
            on_github_click=lambda e: components.show_github_dialog(page),
            on_settings_click=lambda e: self._show_settings_dialog(page),
            status_widget=status_container,
        )

        # Check Ollama status in background on startup
        threading.Thread(
            target=self._check_ollama_status, args=(page,), daemon=True
        ).start()


        # Create version dropdown
        version_dropdown = styles.create_dropdown(
            "MODの対応バージョン",
            list(config.VERSION_TO_PACK_FORMAT.keys()),
            on_select=lambda e: self._handle_version_change(e, page),
        )

        # Create file selection buttons (initially hidden)
        async def open_file_picker(_):
            files = await ft.FilePicker().pick_files(
                allow_multiple=True,
                initial_directory=os.path.expanduser("~\\Downloads"),
                allowed_extensions=["jar"],
                dialog_title="翻訳するMODのjarファイルを選択(複数選択可)",
            )
            if files:
                file_paths = [file.path for file in files if file.path]
                logger.info(f"Files selected via picker: {len(file_paths)} file(s)")
                for fp in file_paths:
                    logger.debug(f"  Selected: {fp}")
                if not file_paths:
                    self.selected_files_text.value = "有効なファイルが選択されませんでした。"
                    self.selected_files_text.update()
                    components.show_error_dialog(
                        page, "エラー", "有効なjarファイルが見つかりませんでした。"
                    )
                    return
                self.file_names = [os.path.basename(fp) for fp in file_paths]
                self.selected_files_text.value = ", ".join(self.file_names)
                self.selected_files_text.update()
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, self.process_files, file_paths, self.file_names, page
                )
            else:
                self.selected_files_text.value = "キャンセルされました!"
                self.selected_files_text.update()

        async def open_clipboard(_):
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, components.select_file_from_clipboard, page, self.process_files
            )

        self.file_button = styles.create_button(
            "翻訳するMODのjarファイルを選択",
            icon=ft.Icons.ATTACH_FILE,
            on_click=open_file_picker,
            visible=False,
        )

        self.clipboard_button = styles.create_button(
            "クリップボードからパスを取得",
            ft.Icons.CONTENT_PASTE,
            on_click=open_clipboard,
            visible=False,
        )

        # Create selected files text
        self.selected_files_text = ft.Text(
            color=config.COLORS["text"],
            size=14,
        )

        # Create main content
        main_content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                version_dropdown,
                ft.Divider(color=config.COLORS["divider"], height=1),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[self.file_button, self.clipboard_button],
                ),
                self.selected_files_text,
            ],
        )

        # Add main content to page
        page.add(
            ft.Container(
                margin=ft.margin.only(top=20),
                content=styles.create_card(main_content),
            )
        )

        # Create loading indicator
        components.make_loading_indicator(page)

        # Set up window resize handler
        page.on_resize = lambda e: self._handle_window_resize(e, page)  # type: ignore[attr-defined]

        # Update the page
        page.update()

        # Show dialog if config file was corrupted on startup
        if config.config_corrupted:
            self._show_corrupted_config_dialog(page)

    def _set_window_icon(self, page: ft.Page) -> None:
        """
        Set the window icon.

        Args:
            page: The page to set the icon for
        """
        try:
            # Get the root directory
            if getattr(sys, "frozen", False):
                # Running as compiled executable
                root_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                root_dir = os.path.abspath(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                )

            # Set the icon
            icon_path = os.path.join(root_dir, "resources", "icon.ico")
            if os.path.exists(icon_path):
                page.window.icon = icon_path
                logger.info(f"Set window icon: {icon_path}")
            else:
                logger.warning(f"Icon file not found: {icon_path}")
        except Exception as e:
            logger.error(f"Error setting window icon: {e}", exc_info=True)

    def _handle_version_change(self, e, page: ft.Page) -> None:
        """
        Handle version dropdown change.

        Args:
            e: Change event
            page: The page
        """
        if e.control.value:
            # Set pack format
            config.pack_format = config.get_pack_format_for_version(e.control.value)
            logger.info(
                f"Version selected: {e.control.value} "
                f"(pack_format={config.pack_format})"
            )

            # Show file selection buttons
            self.file_button.visible = True
            self.clipboard_button.visible = True
            self.file_button.offset = ft.Offset(0, 0)
            self.clipboard_button.offset = ft.Offset(0, 0)

            page.update()
        else:
            # Hide file selection buttons
            self.file_button.visible = False
            self.clipboard_button.visible = False

            page.update()

    def _check_ollama_status(self, page: ft.Page) -> None:
        """Check Ollama availability and update the status indicator.

        Args:
            page: The page containing the status indicator.
        """
        if self._status_dot is None or self._status_text is None:
            return

        ollama_running, model_ok = translator.check_ollama_availability()

        if not ollama_running:
            state = components.OLLAMA_STATUS_ERROR
        elif not model_ok:
            state = components.OLLAMA_STATUS_NO_MODEL
        else:
            state = components.OLLAMA_STATUS_OK

        components.update_ollama_status_indicator(
            self._status_dot, self._status_text, state, page
        )

    def _show_settings_dialog(self, page: ft.Page) -> None:
        """Show the Ollama settings dialog.

        Args:
            page: The page.
        """

        def on_settings_saved():
            """Callback when settings are saved."""
            translator.reset_ollama_client()
            logger.info("Ollama client reset after settings update")
            # Reset indicator to "checking" then re-check in background
            if self._status_dot and self._status_text:
                components.update_ollama_status_indicator(
                    self._status_dot,
                    self._status_text,
                    components.OLLAMA_STATUS_CHECKING,
                    page,
                )
            threading.Thread(
                target=self._check_ollama_status, args=(page,), daemon=True
            ).start()
            components.show_dialog(
                page,
                "設定保存完了",
                f"Ollama設定が保存されました。\n\n"
                f"サーバー: {config.OLLAMA_BASE_URL}\n"
                f"モデル: {config.OLLAMA_MODEL}",
            )

        components.show_ollama_settings_dialog(page, on_settings_saved)

    def _show_corrupted_config_dialog(self, page: ft.Page) -> None:
        """Show a dialog when ollama_config.json is corrupted.

        Args:
            page: The page to show the dialog on.
        """
        def recreate(e):
            page.pop_dialog()
            config.save()
            config.load()
            logger.info("Recreated corrupted ollama_config.json with defaults")

        def cancel(e):
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text("設定ファイルのエラー"),
            content=ft.Text(
                "設定ファイル (ollama_config.json) が壊れています。\n"
                "新しく作成しますか？（デフォルト値に戻ります）"
            ),
            actions=[
                ft.TextButton("キャンセル", on_click=cancel),
                ft.ElevatedButton("新規作成", on_click=recreate),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        page.show_dialog(dialog)

    def _handle_window_resize(self, e, page: ft.Page) -> None:
        """Handle window resize event.

        Args:
            e: Resize event.
            page: The page.
        """
        components.initialize_page_data(page)

        progress_container = page.data.get(components.PROGRESS_CONTAINER_KEY)

        if progress_container and isinstance(progress_container, ft.Container):
            if page.window is not None and page.window.height is not None:
                progress_container.height = page.window.height - 150
                page.update()

    def process_files(
        self, file_paths: List[str], file_names: List[str], page: ft.Page
    ) -> None:
        """
        Process the selected files.

        Args:
            file_paths: List of file paths
            file_names: List of file names
            page: The page
        """
        process_start = time.time()
        logger.info(
            f"Processing {len(file_paths)} JAR file(s): "
            + ", ".join(file_names)
        )
        try:
            # Check Ollama availability before doing any work
            ollama_running, model_ok = translator.check_ollama_availability()
            if not ollama_running:
                components.show_ollama_not_found_dialog(page)
                return
            if not model_ok:
                components.show_model_not_found_dialog(page, config.OLLAMA_MODEL)
                return

            # Hide selection UI
            components.hide_selection_ui(page)

            # Hide loading indicator
            components.hide_loading(page)

            # Initialize directories
            file_manager.init_directory(config.TEMP_DIR)
            file_manager.init_directory(config.OUTPUT_DIR)
            logger.info("Initialized temp and output directories")

            # Create extraction progress UI
            extract_pb, extract_info = components.make_extract_progress(page)
            total_files = len(file_paths)

            # Extract JAR files
            unzipped_file_paths = []
            for i, file_path in enumerate(file_paths):
                # Update progress
                current_file = i + 1
                file_name = os.path.basename(file_path)
                components.update_extract_progress(
                    extract_pb, current_file, total_files, extract_info, page, file_name
                )

                # Extract JAR file
                unzipped_path = file_manager.recursive_unzip_jar(file_path)
                if unzipped_path:
                    unzipped_file_paths.append(unzipped_path)

            # Update extraction progress
            extract_info.value = "解凍完了"
            page.update()

            # Wait a bit to show completion
            time.sleep(1)

            # Hide extraction progress
            components.hide_extract_progress(page)

            # Find en_us.json files
            en_us_json_files = self._find_language_files()

            if not en_us_json_files:
                components.show_error_dialog(
                    page, "エラー", "en_us.jsonファイルが見つかりませんでした。"
                )
                return

            # Clean temp directory
            self._clean_temp_directory(en_us_json_files)

            # Generate resource pack
            if not resource_pack.generate_resource_pack(en_us_json_files, page):
                components.show_error_dialog(
                    page, "エラー", "リソースパックの生成に失敗しました。"
                )
                return

            # Copy assets folders
            file_manager.copy_assets_folders(config.TEMP_DIR, en_us_json_files)

            # Find language files that need translation
            _, lang_files_to_translate = file_manager.search_language_files()

            if not lang_files_to_translate:
                components.show_dialog(
                    page, "完了", "翻訳対象のファイルが見つかりませんでした。"
                )
                self._finish_translation(page, 0)
                return

            # Translate language files
            if translator.translate_all_files(lang_files_to_translate, page):
                elapsed = time.time() - process_start
                logger.info(
                    f"All processing completed in {elapsed:.1f}s "
                    f"({len(lang_files_to_translate)} file(s) translated)"
                )
                components.show_dialog(page, "完了", "全ての翻訳が完了しました。")
                self._finish_translation(page, len(lang_files_to_translate))
            else:
                components.show_error_dialog(page, "エラー", "翻訳に失敗しました。")
                components.show_selection_ui(page)

        except (FileOperationError, ResourcePackError, TranslationError, UIError) as e:
            logger.error(f"Error processing files: {e}", exc_info=True)
            components.show_error_dialog(
                page, "エラー", f"処理中にエラーが発生しました: {str(e)}"
            )
            components.show_selection_ui(page)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            components.show_error_dialog(
                page, "エラー", f"予期せぬエラーが発生しました: {str(e)}"
            )
            components.show_selection_ui(page)

    def _find_language_files(self) -> List[str]:
        """
        Find en_us.json files in the temp directory.

        Returns:
            List of en_us.json file paths
        """
        en_us_json_files = []

        try:
            # Find all en_us.json files
            en_us_json_files = [
                path
                for path in glob.glob(
                    os.path.join(config.TEMP_DIR, "**", "en_us.json"), recursive=True
                )
                if path
            ]

            logger.info(f"Found {len(en_us_json_files)} en_us.json file(s) in temp directory")
            for f in en_us_json_files:
                logger.debug(f"  en_us.json: {f}")
        except Exception as e:
            logger.error(f"Error finding language files: {e}", exc_info=True)
            raise FileOperationError("Failed to find language files") from e

        return en_us_json_files

    def _clean_temp_directory(self, en_us_json_files: List[str]) -> None:
        """
        Clean the temp directory, keeping only necessary files.

        Args:
            en_us_json_files: List of en_us.json file paths
        """
        try:
            # Create list of files to keep
            files_to_keep = []

            for en_us_json_file in en_us_json_files:
                # Keep en_us.json
                files_to_keep.append(en_us_json_file)

                # Keep ja_jp.json if it exists
                ja_jp_file = os.path.join(
                    os.path.dirname(en_us_json_file), "ja_jp.json"
                )
                if os.path.exists(ja_jp_file):
                    files_to_keep.append(ja_jp_file)

            # Clean directory
            file_manager.clean_directory(config.TEMP_DIR, files_to_keep)
        except Exception as e:
            logger.error(f"Error cleaning temp directory: {e}", exc_info=True)
            raise FileOperationError("Failed to clean temp directory") from e

    def _finish_translation(self, page: ft.Page, success_count: int) -> None:
        """
        Finish the translation process.

        Args:
            page: The page
            success_count: Number of successfully translated files
        """
        try:
            # Show notification
            if success_count > 0:
                logger.info(f"{success_count} MODs translated successfully")

                try:
                    # Get icon path
                    if getattr(sys, "frozen", False):
                        base_dir = os.path.dirname(sys.executable)
                    else:
                        base_dir = os.path.dirname(
                            os.path.dirname(os.path.dirname(__file__))
                        )

                    icon_path = os.path.join(base_dir, "resources", "icon.ico")

                    if not os.path.exists(icon_path):
                        logger.warning(f"Notification icon not found: {icon_path}")
                        icon_path = ""

                    # 通知機能が使えるかチェック
                    if (
                        notification is not None
                        and hasattr(notification, "notify")
                        and callable(notification.notify)
                    ):
                        # Show notification
                        notification.notify(
                            title="翻訳完了",
                            message=f"{success_count}個のMODの翻訳が完了しました。",
                            app_name="MC-MOD Translating tool",
                            app_icon=icon_path,
                            timeout=10,
                        )
                    else:
                        logger.warning("通知機能がこのシステムでは利用できません")
                except ImportError:
                    logger.warning("Plyer library not found. Skipping notification.")
                except Exception as e:
                    logger.error(f"Failed to send notification: {e}", exc_info=True)

            # Open output directory
            os.startfile(os.path.dirname(config.OUTPUT_DIR)) # type: ignore

            # Close the window
            # _finish_translation runs in a thread (via run_in_executor),
            # so we must schedule the async close() on the main event loop.
            if self._loop:
                asyncio.run_coroutine_threadsafe(page.window.close(), self._loop)
        except Exception as e:
            logger.error(f"Error finishing translation: {e}", exc_info=True)
            raise UIError("Failed to finish translation") from e


def start_app(page: ft.Page) -> None:
    """
    Start the application.

    Args:
        page: The page
    """
    app = MinecraftModTranslatorApp()
    app.initialize_ui(page)
