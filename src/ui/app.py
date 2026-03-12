"""Main UI application for the Minecraft MOD Translator Tool."""

import glob
import logging
import os
import sys
import time
import webbrowser
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

    def initialize_ui(self, page: ft.Page) -> None:
        """Initialize the UI.

        Args:
            page: The page to initialize.
        """
        page.window.width = DEFAULT_WINDOW_WIDTH
        page.window.height = DEFAULT_WINDOW_HEIGHT
        page.theme = styles.create_theme()
        page.padding = DEFAULT_WINDOW_PADDING
        page.bgcolor = config.COLORS["background"]

        self._set_window_icon(page)

        page.appbar = styles.create_app_bar(
            page,
            on_help_click=lambda e: components.show_dialog(
                page, "このアプリについて", TEXT_ABOUT_DIALOG
            ),
            on_github_click=lambda e: components.show_github_dialog(page),
            on_settings_click=lambda e: self._show_settings_dialog(page),
        )

        # Create file picker
        pick_file_dialog = ft.FilePicker(
            on_result=lambda e: self._handle_file_selection(e, page)
        )
        page.overlay.append(pick_file_dialog)

        # Create version dropdown
        version_dropdown = styles.create_dropdown(
            "MODの対応バージョン",
            list(config.VERSION_TO_PACK_FORMAT.keys()),
            on_change=lambda e: self._handle_version_change(e, page),
        )

        # Create file selection buttons (initially hidden)
        self.file_button = styles.create_button(
            "翻訳するMODのjarファイルを選択",
            ft.Icons.ATTACH_FILE,
            on_click=lambda _: pick_file_dialog.pick_files(
                allow_multiple=True,
                initial_directory=os.path.expanduser("~\\Downloads"),
                allowed_extensions=["jar"],
                dialog_title="翻訳するMODのjarファイルを選択(複数選択可)",
            ),
            visible=False,
        )

        self.clipboard_button = styles.create_button(
            "クリップボードからパスを取得",
            ft.Icons.CONTENT_PASTE,
            on_click=lambda _: components.select_file_from_clipboard(
                page, self.process_files
            ),
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

    def _handle_file_selection(self, e, page: ft.Page) -> None:
        """Handle file selection.

        Args:
            e: File picker result event.
            page: The page.
        """
        if e.files:
            file_paths = [file.path for file in e.files if file.path]

            if not file_paths:
                self.selected_files_text.value = "有効なファイルが選択されませんでした。"  # type: ignore[attr-defined]
                self.selected_files_text.update()  # type: ignore[attr-defined]
                components.show_error_dialog(
                    page, "エラー", "有効なjarファイルが見つかりませんでした。"
                )
                return

            self.file_names = [os.path.basename(file_path) for file_path in file_paths]

            self.selected_files_text.value = ", ".join(self.file_names)  # type: ignore[attr-defined]
            self.selected_files_text.update()  # type: ignore[attr-defined]

            self.process_files(file_paths, self.file_names, page)
        else:
            self.selected_files_text.value = "キャンセルされました!"  # type: ignore[attr-defined]
            self.selected_files_text.update()  # type: ignore[attr-defined]

    def _show_settings_dialog(self, page: ft.Page) -> None:
        """Show the OpenRouter settings dialog.

        Args:
            page: The page.
        """

        def on_settings_saved():
            """Callback when settings are saved."""
            translator.reset_openrouter_client()
            logger.info("OpenRouter client reset after settings update")
            components.show_dialog(
                page,
                "設定保存完了",
                f"OpenRouter設定が保存されました。\n\n"
                f"モデル: {config.OPENROUTER_MODEL}\n"
                f"フォールバック数: {len(config.FALLBACK_MODELS)}",
            )

        components.show_openrouter_settings_dialog(page, on_settings_saved)

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
        try:
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
                components.show_dialog(page, "完了", "全ての翻訳が完了しました。")
                self._finish_translation(page, len(lang_files_to_translate))
            else:
                components.show_error_dialog(page, "エラー", "翻訳に失敗しました。")
                sys.exit(1)

        except (FileOperationError, ResourcePackError, TranslationError, UIError) as e:
            logger.error(f"Error processing files: {e}", exc_info=True)
            components.show_error_dialog(
                page, "エラー", f"処理中にエラーが発生しました: {str(e)}"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            components.show_error_dialog(
                page, "エラー", f"予期せぬエラーが発生しました: {str(e)}"
            )
            sys.exit(1)

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

            logger.debug(f"Found {len(en_us_json_files)} en_us.json files")
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
            os.startfile(os.path.dirname(config.OUTPUT_DIR))

            # Close the window
            page.window.close()

            # Exit the program
            sys.exit(0)
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
