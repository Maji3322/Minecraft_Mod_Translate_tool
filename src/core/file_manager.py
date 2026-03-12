"""File management operations for the application."""

import glob
import logging
import os
import shutil
import zipfile
from typing import List, Optional, Tuple

from ..utils.config import config
from ..utils.exceptions import FileOperationError

logger = logging.getLogger(__name__)


def init_directory(path: str) -> None:
    """Initialize a directory by removing it if exists and creating new one.

    Args:
        path: The path to the directory to initialize.

    Raises:
        FileOperationError: If the directory cannot be initialized.
    """
    logger.info(f"Initializing directory: {path}")

    try:
        if os.path.exists(path):
            logger.debug(f"{path} exists. Removing it.")
            shutil.rmtree(path)

        os.makedirs(path)
        logger.debug(f"Created {path}")
    except OSError as e:
        error_msg = f"Failed to initialize directory {path}: {str(e)}"
        logger.error(error_msg)
        raise FileOperationError(error_msg) from e


def recursive_unzip_jar(jar_path: str) -> Optional[str]:
    """Recursively unzip a JAR file, including nested JARs in META-INF/jars.

    Args:
        jar_path: The path to the JAR file to unzip.

    Returns:
        The path to directory containing unzipped files, or None if doesn't exist.

    Raises:
        FileOperationError: If the JAR file cannot be unzipped.
    """
    if not os.path.exists(jar_path):
        logger.error(f"{jar_path} not found. Skipping.")
        return None

    logger.info(f"Unzipping {jar_path}")

    if not os.path.exists(config.TEMP_DIR):
        os.makedirs(config.TEMP_DIR)

    base_name = os.path.splitext(os.path.basename(jar_path))[0]
    jar_folder = os.path.join(os.getcwd(), config.TEMP_DIR, base_name)
    os.makedirs(jar_folder, exist_ok=True)

    _, ext = os.path.splitext(jar_path)
    if ext.lower() == ".jar":
        zip_path = jar_folder + ".zip"
        shutil.copy2(jar_path, zip_path)
    else:
        zip_path = jar_path

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            logger.debug(f"Extracting {zip_path}")
            zip_file.extractall(jar_folder)
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        logger.error(f"Extraction error: {zip_path} - {str(e)}")
        return jar_folder

    if ext.lower() == ".jar" and os.path.exists(zip_path):
        os.remove(zip_path)

    _extract_nested_jars(jar_folder)

    return jar_folder


def _extract_nested_jars(jar_folder: str) -> None:
    """Extract nested JAR files from META-INF/jars directory.

    Args:
        jar_folder: The folder containing the extracted JAR files.
    """
    meta_jars_path = os.path.join(jar_folder, "META-INF", "jars")
    if not os.path.exists(meta_jars_path):
        return

    for root, _, files in os.walk(meta_jars_path):
        for file in files:
            if file.endswith(".jar"):
                inner_jar_path = os.path.join(root, file)
                try:
                    inner_base_name = os.path.splitext(file)[0][:30]
                    inner_jar_folder = os.path.join(jar_folder, f"__{inner_base_name}")
                    os.makedirs(inner_jar_folder, exist_ok=True)

                    with zipfile.ZipFile(inner_jar_path, "r") as inner_zip:
                        logger.debug(f"Extracting inner JAR: {inner_jar_path}")
                        inner_zip.extractall(inner_jar_folder)
                except (zipfile.BadZipFile, FileNotFoundError, OSError) as e:
                    logger.error(f"Inner JAR extraction error: {inner_jar_path} - {str(e)}")
                    continue


def clean_directory(root_dir: str, files_to_keep: List[str]) -> None:
    """Clean a directory by removing all files except those in files_to_keep.

    Args:
        root_dir: The root directory to clean.
        files_to_keep: A list of file paths to keep.

    Raises:
        FileOperationError: If the directory cannot be cleaned.
    """
    try:
        for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if file_path not in files_to_keep:
                    os.remove(file_path)

            for dirname in dirnames:
                dir_path = os.path.join(dirpath, dirname)
                should_keep = any(
                    os.path.commonpath([file_path, dir_path]) == dir_path
                    for file_path in files_to_keep
                )
                if not should_keep:
                    shutil.rmtree(dir_path)

        logger.info(f"Cleaned directory: {root_dir}")
    except (OSError, shutil.Error) as e:
        error_msg = f"Failed to clean directory {root_dir}: {str(e)}"
        logger.error(error_msg)
        raise FileOperationError(error_msg) from e


def copy_assets_folders(root_dir: str, json_file_paths: List[str]) -> None:
    """Copy assets folders from source directories to output directory.

    Args:
        root_dir: The root directory containing the assets folders.
        json_file_paths: A list of JSON file paths.

    Raises:
        FileOperationError: If the assets folders cannot be copied.
    """
    try:
        translate_rp_dir = os.path.join(os.path.dirname(root_dir), config.OUTPUT_DIR)
        assets_dir = os.path.join(translate_rp_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        for json_file_path in json_file_paths:
            src_assets_dir = os.path.dirname(os.path.dirname(json_file_path))
            dest_dirname = os.path.basename(src_assets_dir)
            dest_dir = os.path.join(assets_dir, dest_dirname)

            if os.path.exists(dest_dir):
                _merge_folders(src_assets_dir, dest_dir)
                logger.info(f"Merged assets folder: {dest_dir}")
            else:
                shutil.copytree(src_assets_dir, dest_dir)
                logger.info(f"Copied assets folder: {dest_dir}")
    except (OSError, shutil.Error) as e:
        error_msg = f"Failed to copy assets folders: {str(e)}"
        logger.error(error_msg)
        raise FileOperationError(error_msg) from e


def _merge_folders(src_dir: str, dest_dir: str) -> None:
    """Merge source folder into destination folder.

    Args:
        src_dir: Source directory path.
        dest_dir: Destination directory path.
    """
    for root, _, files in os.walk(src_dir):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_dir, os.path.relpath(src_file, src_dir))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)


def search_language_files() -> Tuple[List[str], List[str]]:
    """Search for language files in the output directory.

    Returns:
        A tuple containing:
        - A list of en_us.json file paths.
        - A list of en_us.json files needing translation (no ja_jp.json).

    Raises:
        FileOperationError: If the language files cannot be searched.
    """
    try:
        en_us_json_paths = glob.glob(
            os.path.join(config.OUTPUT_DIR, "**", "en_us.json"), recursive=True
        )

        if not en_us_json_paths:
            logger.info("No en_us.json files found.")
            return [], []

        need_translation_paths = []

        for en_us_path in en_us_json_paths:
            ja_jp_json_path = os.path.join(os.path.dirname(en_us_path), "ja_jp.json")

            if not os.path.exists(ja_jp_json_path):
                logger.info(
                    f"No ja_jp.json found for {en_us_path}. Adding to translation list."
                )
                need_translation_paths.append(en_us_path)
            else:
                logger.info(f"ja_jp.json exists for {en_us_path}. Skipping.")

        return en_us_json_paths, need_translation_paths
    except Exception as e:
        error_msg = f"Failed to search language files: {str(e)}"
        logger.error(error_msg)
        raise FileOperationError(error_msg) from e