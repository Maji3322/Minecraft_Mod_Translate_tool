"""
Translation functionality for the application.
"""

import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from openai import OpenAI
from tqdm import tqdm

from ..utils.config import config
from ..utils.exceptions import TranslationError

logger = logging.getLogger(__name__)

# Type variable for generic function
T = TypeVar("T")

# Shared OpenAI client instance for connection pooling
_openrouter_client: Optional[OpenAI] = None


def get_openrouter_client() -> OpenAI:
    """
    Get or create a shared OpenRouter client instance.
    
    This function ensures a single client instance is reused across all
    translation calls for efficient connection pooling.
    
    Returns:
        OpenAI client configured for OpenRouter
        
    Raises:
        TranslationError: If API key is not configured
    """
    global _openrouter_client
    
    # APIキーのチェック（空白や空文字列も検出）
    if not config.OPENROUTER_API_KEY or not config.OPENROUTER_API_KEY.strip():
        raise TranslationError(
            "OpenRouter API key is not set or is empty. Please set OPENROUTER_API_KEY in .env file."
        )
    
    # クライアントがまだ作成されていない場合は作成
    if _openrouter_client is None:
        _openrouter_client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY
        )
        logger.info(f"Created OpenRouter client with model: {config.OPENROUTER_MODEL}")
    
    return _openrouter_client


def retry_on_timeout(max_retries: int = 3, base_delay: int = 2) -> Callable:
    """
    Decorator to retry a function on timeout with exponential backoff.

    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Translation error (possible timeout): {e}")
                        raise TranslationError(
                            f"Failed after {max_retries} retries"
                        ) from e

                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** (retries - 1)) + random.uniform(0, 1)
                    logger.warning(
                        f"Translation error. Retrying in {delay:.2f} seconds (attempt {retries})..."
                    )
                    time.sleep(delay)

            # このコードには到達しないはずだが、型チェックのために必要
            raise RuntimeError("Unexpected exit from retry loop")

        return wrapper

    return decorator


@retry_on_timeout(
    max_retries=config.MAX_TRANSLATION_RETRIES,
    base_delay=config.TRANSLATION_RETRY_BASE_DELAY,
)
def translate_text(client: OpenAI, text: str, model: str = "") -> str:
    """
    Translate text using OpenRouter LLM with retry and fallback functionality.

    Args:
        client: The OpenAI client configured for OpenRouter
        text: The text to translate
        model: Optional specific model to use (overrides config)

    Returns:
        The translated text

    Raises:
        TranslationError: If the translation fails after retries
    """
    # Use provided model or fall back to configured model
    current_model = model if model else config.OPENROUTER_MODEL
    
    # Try with primary model first, then fallbacks
    models_to_try = [current_model] + config.FALLBACK_MODELS
    last_error = None
    
    for attempt_model in models_to_try:
        if not attempt_model:
            continue
            
        try:
            logger.info(f"Translating with model: {attempt_model}")
            # LLMを使用した翻訳プロンプト
            response = client.chat.completions.create(
                model=attempt_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator specializing in video game localization. "
                        "Translate the given English text to Japanese. "
                        "Maintain game terminology, preserve special characters like %, $, and formatting. "
                        "Return ONLY the translated text without any explanations or additional content.",
                    },
                    {"role": "user", "content": f"Translate to Japanese: {text}"},
                ],
                temperature=0.3,  # 低めの温度で一貫性のある翻訳を得る
                max_tokens=500,
            )

            result = response.choices[0].message.content

            if result is None:
                logger.warning(f"Translation returned None for text: {text}")
                return text

            # 翻訳結果をクリーンアップ
            result = result.strip()

            # 一般的な翻訳の問題を修正
            result = result.replace("％", " %").replace("$ ", "$")

            return result

        except Exception as e:
            error_msg = str(e).lower()
            last_error = e
            
            # レート制限エラーの場合はフォールバックモデルを試す
            if "429" in error_msg or "rate limit" in error_msg:
                logger.warning(f"Rate limit hit with model {attempt_model}, trying fallback...")
                continue
            
            # 認証エラーやモデルが見つからない場合は即座に失敗
            if any(
                keyword in error_msg
                for keyword in ["authentication", "unauthorized", "invalid api key", "not found", "model"]
            ):
                logger.error(f"Non-retryable error during LLM translation: {e}")
                raise TranslationError(f"LLM translation failed (non-retryable): {e}") from e
            
            # その他のエラーはリトライ可能として扱う
            logger.error(f"Error during LLM translation with model {attempt_model}: {e}", exc_info=True)
            raise TranslationError(f"LLM translation failed: {e}") from e
    
    # All models failed
    if last_error:
        logger.error(f"All models failed, last error: {last_error}")
        raise TranslationError(f"Translation failed with all models: {last_error}") from last_error
    else:
        raise TranslationError("No models configured for translation")


def translate_json_file(lang_file_path: str, page=None) -> bool:
    """
    Translate a JSON language file using OpenRouter LLM and save the result as ja_jp.json.

    Args:
        lang_file_path: Path to the en_us.json file
        page: The UI page object (optional)

    Returns:
        True if translation was successful, False otherwise

    Raises:
        TranslationError: If the translation fails
    """
    start_time = time.time()

    # 変数を初期化しておく
    progressbar = None
    info_msg = None

    try:
        # 共有クライアントを取得（APIキーチェック含む）
        client = get_openrouter_client()

        logger.info(
            f"Starting LLM translation of {lang_file_path} using model: {config.OPENROUTER_MODEL}"
        )

        # Read the source JSON file
        with open(lang_file_path, "r", encoding="utf-8") as f:
            en_json = json.load(f)

        # Create empty target JSON
        ja_json = {}

        # Count total strings to translate
        def find_strings(json_data: Dict) -> List[str]:
            """Find all strings in a nested JSON structure."""
            strings = []
            for value in json_data.values():
                if isinstance(value, str):
                    strings.append(value)
                elif isinstance(value, dict):
                    strings.extend(find_strings(value))
            return strings

        total_strings = len(find_strings(en_json))

        # Set up progress tracking
        if page:
            from ..ui.components import make_progress_bar, update_progress_bar

            progressbar, info_msg = make_progress_bar(page, lang_file_path)

        translated_strings = 0
        pbar = tqdm(total=total_strings, position=0, leave=True)

        # Translate the JSON
        for key, value in en_json.items():
            if isinstance(value, str):
                try:
                    result = translate_text(client, value)
                    ja_json[key] = result
                    translated_strings += 1

                    # Update progress
                    if page and progressbar and info_msg:
                        from ..ui.components import update_progress_bar

                        update_progress_bar(
                            progressbar,
                            translated_strings,
                            total_strings,
                            info_msg,
                            page,
                            start_time,
                        )

                    pbar.update(1)
                except Exception as e:
                    logger.error(
                        f"Error translating {lang_file_path}: {e}", exc_info=True
                    )
                    raise TranslationError(
                        f"Failed to translate {lang_file_path}"
                    ) from e
            elif isinstance(value, dict):
                ja_dict = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        try:
                            result = translate_text(client, sub_value)
                            ja_dict[sub_key] = result
                            translated_strings += 1
                            pbar.update(1)
                        except Exception as e:
                            logger.error(
                                f"Error translating {lang_file_path}: {e}",
                                exc_info=True,
                            )
                            raise TranslationError(
                                f"Failed to translate {lang_file_path}"
                            ) from e
                    else:
                        ja_dict[sub_key] = sub_value
                ja_json[key] = ja_dict

        # Write the translated JSON
        output_path = lang_file_path.replace("en_us.json", "ja_jp.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ja_json, f, indent=4, ensure_ascii=False)

        logger.info(f"Completed LLM translation of {lang_file_path}")

        # Update progress info
        if page and info_msg:
            info_msg.value = (
                f"完了：{translated_strings}/{total_strings}箇所を翻訳しました。"
            )
            page.update()

        return True

    except (json.JSONDecodeError, IOError, TranslationError) as e:
        logger.error(f"Error translating {lang_file_path}: {e}", exc_info=True)
        raise TranslationError(f"Failed to translate {lang_file_path}") from e


def translate_all_files(lang_file_paths: List[str], page=None) -> bool:
    """
    Translate all language files in parallel.

    Args:
        lang_file_paths: List of paths to en_us.json files
        page: The UI page object (optional)

    Returns:
        True if all translations were successful, False otherwise

    Raises:
        TranslationError: If any translation fails
    """
    if not lang_file_paths:
        logger.info("No files to translate.")
        return True

    try:
        with ThreadPoolExecutor() as executor:
            # Map each file to the translate_json_file function with the page argument
            futures = [
                executor.submit(translate_json_file, path, page)
                for path in lang_file_paths
            ]

            # Wait for all futures to complete
            for future in futures:
                if not future.result():
                    logger.error("Translation failed for one or more files.")
                    return False

        logger.info("All translations completed successfully.")
        return True

    except Exception as e:
        logger.error(f"Error in translation process: {e}", exc_info=True)
        raise TranslationError("Failed to translate files") from e
