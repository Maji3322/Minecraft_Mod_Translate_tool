"""Translation functionality for the application."""

import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

from openai import OpenAI
from tqdm import tqdm

from ..utils.config import config
from ..utils.exceptions import TranslationError

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Shared OpenAI client instance for connection pooling
_openrouter_client: Optional[OpenAI] = None

# Translation prompt constants
TRANSLATION_SYSTEM_PROMPT = (
    "You are a professional translator specializing in video game localization. "
    "Translate the given English text to Japanese. "
    "Maintain game terminology, preserve special characters like %, $, and formatting. "
    "Return ONLY the translated text without any explanations or additional content."
)

# Error keywords for authentication issues
AUTH_ERROR_KEYWORDS = [
    "authentication",
    "unauthorized",
    "invalid api key",
    "api key",
    "access denied",
]

# Error keywords for rate limit issues
RATE_LIMIT_KEYWORDS = ["429", "402", "rate limit"]


def get_openrouter_client() -> OpenAI:
    """Get or create a shared OpenRouter client instance.

    This function ensures a single client instance is reused across all
    translation calls for efficient connection pooling.

    Returns:
        OpenAI client configured for OpenRouter.

    Raises:
        TranslationError: If API key is not configured.
    """
    global _openrouter_client

    if not config.OPENROUTER_API_KEY or not config.OPENROUTER_API_KEY.strip():
        raise TranslationError(
            "OpenRouter API key is not set or is empty. "
            "Please configure your OpenRouter API key in the application "
            "settings dialog (⚙️ icon)."
        )

    if _openrouter_client is None:
        _openrouter_client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL, api_key=config.OPENROUTER_API_KEY
        )
        logger.info(f"Created OpenRouter client with model: {config.OPENROUTER_MODEL}")

    return _openrouter_client


def reset_openrouter_client() -> None:
    """Reset the cached OpenRouter client instance.

    This should be called when the API key changes to ensure
    the next translation uses the new API key.
    """
    global _openrouter_client
    _openrouter_client = None
    logger.info("Reset OpenRouter client cache")


def retry_on_timeout(max_retries: int = 3, base_delay: int = 2) -> Callable:
    """Decorator to retry a function on timeout with exponential backoff.

    Args:
        max_retries: Maximum number of retries.
        base_delay: Base delay in seconds.

    Returns:
        Decorated function.
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

                    delay = base_delay * (2 ** (retries - 1)) + random.uniform(0, 1)
                    logger.warning(
                        f"Translation error. Retrying in {delay:.2f} seconds "
                        f"(attempt {retries})..."
                    )
                    time.sleep(delay)

            raise RuntimeError("Unexpected exit from retry loop")

        return wrapper

    return decorator


@retry_on_timeout(
    max_retries=config.MAX_TRANSLATION_RETRIES,
    base_delay=config.TRANSLATION_RETRY_BASE_DELAY,
)
def translate_text(client: OpenAI, text: str, model: str = "") -> str:
    """Translate text using OpenRouter LLM with retry and fallback.

    Args:
        client: The OpenAI client configured for OpenRouter.
        text: The text to translate.
        model: Optional specific model to use (overrides config).

    Returns:
        The translated text.

    Raises:
        TranslationError: If the translation fails after retries.
    """
    current_model = model if model else config.OPENROUTER_MODEL
    models_to_try = [current_model] + config.FALLBACK_MODELS
    last_error = None

    for attempt_model in models_to_try:
        if not attempt_model:
            continue

        try:
            logger.info(f"Translating with model: {attempt_model}")
            result = _perform_translation(client, text, attempt_model)
            return _clean_translation_result(result, text)

        except Exception as e:
            last_error = e
            error_msg = str(e).lower()

            if _is_rate_limit_error(error_msg):
                logger.warning(
                    f"Rate limit hit with model {attempt_model}, trying fallback..."
                )
                continue

            if _is_auth_error(error_msg):
                logger.error(f"Non-retryable authentication error: {e}")
                raise TranslationError(
                    f"LLM translation failed (non-retryable auth error): {e}"
                ) from e

            logger.warning(
                f"Error with model {attempt_model}: {e}. Trying fallback...",
                exc_info=True,
            )
            continue

    if last_error:
        logger.error(f"All models failed, last error: {last_error}")
        raise TranslationError(
            f"Translation failed with all models: {last_error}"
        ) from last_error
    else:
        raise TranslationError("No models configured for translation")


def _perform_translation(client: OpenAI, text: str, model: str) -> str:
    """Perform actual translation API call.

    Args:
        client: The OpenAI client.
        text: Text to translate.
        model: Model to use.

    Returns:
        Translated text.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Translate to Japanese: {text}"},
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return response.choices[0].message.content


def _clean_translation_result(result: Optional[str], original_text: str) -> str:
    """Clean and validate translation result.

    Args:
        result: The translation result from API.
        original_text: Original text (fallback if result is None).

    Returns:
        Cleaned translation text.
    """
    if result is None:
        logger.warning(f"Translation returned None for text: {original_text}")
        return original_text

    result = result.strip()
    result = result.replace("％", " %").replace("$ ", "$")
    return result


def _is_rate_limit_error(error_msg: str) -> bool:
    """Check if error message indicates rate limit.

    Args:
        error_msg: Lowercase error message.

    Returns:
        True if rate limit error.
    """
    return any(keyword in error_msg for keyword in RATE_LIMIT_KEYWORDS)


def _is_auth_error(error_msg: str) -> bool:
    """Check if error message indicates authentication issue.

    Args:
        error_msg: Lowercase error message.

    Returns:
        True if authentication error.
    """
    return any(keyword in error_msg for keyword in AUTH_ERROR_KEYWORDS)


def translate_json_file(lang_file_path: str, page=None) -> bool:
    """Translate a JSON language file using OpenRouter LLM to ja_jp.json.

    Args:
        lang_file_path: Path to the en_us.json file.
        page: The UI page object (optional).

    Returns:
        True if translation was successful, False otherwise.

    Raises:
        TranslationError: If the translation fails.
    """
    start_time = time.time()

    try:
        client = get_openrouter_client()

        logger.info(
            f"Starting LLM translation of {lang_file_path} "
            f"using model: {config.OPENROUTER_MODEL}"
        )

        with open(lang_file_path, "r", encoding="utf-8") as f:
            en_json = json.load(f)

        ja_json = {}
        total_strings = _count_translatable_strings(en_json)

        progressbar, info_msg = _setup_progress_tracking(page, lang_file_path)
        translated_strings = 0
        pbar = tqdm(total=total_strings, position=0, leave=True)

        for key, value in en_json.items():
            if isinstance(value, str):
                ja_json[key], translated_strings = _translate_and_update_progress(
                    client,
                    value,
                    translated_strings,
                    total_strings,
                    pbar,
                    page,
                    progressbar,
                    info_msg,
                    start_time,
                    lang_file_path,
                )
            elif isinstance(value, dict):
                ja_json[key], translated_strings = _translate_nested_dict(
                    client,
                    value,
                    translated_strings,
                    total_strings,
                    pbar,
                    page,
                    progressbar,
                    info_msg,
                    start_time,
                    lang_file_path,
                )
            else:
                ja_json[key] = value

        _save_translated_json(lang_file_path, ja_json)
        _finalize_progress(page, info_msg, translated_strings, total_strings)

        logger.info(f"Completed LLM translation of {lang_file_path}")
        return True

    except (json.JSONDecodeError, IOError, TranslationError) as e:
        logger.error(f"Error translating {lang_file_path}: {e}", exc_info=True)
        raise TranslationError(f"Failed to translate {lang_file_path}") from e


def _count_translatable_strings(json_data: Dict) -> int:
    """Count all translatable strings in a nested JSON structure.

    Args:
        json_data: JSON dictionary to count strings in.

    Returns:
        Number of translatable strings.
    """
    count = 0
    for value in json_data.values():
        if isinstance(value, str):
            count += 1
        elif isinstance(value, dict):
            count += _count_translatable_strings(value)
    return count


def _setup_progress_tracking(page, lang_file_path):
    """Set up progress tracking UI components.

    Args:
        page: The UI page object.
        lang_file_path: Path to the file being translated.

    Returns:
        Tuple of (progressbar, info_msg) or (None, None).
    """
    if page:
        from ..ui.components import make_progress_bar

        return make_progress_bar(page, lang_file_path)
    return None, None


def _translate_and_update_progress(
    client,
    text,
    translated_count,
    total_count,
    pbar,
    page,
    progressbar,
    info_msg,
    start_time,
    lang_file_path,
):
    """Translate text and update progress indicators.

    Args:
        client: OpenAI client.
        text: Text to translate.
        translated_count: Current count of translated strings.
        total_count: Total strings to translate.
        pbar: Progress bar object.
        page: UI page object.
        progressbar: UI progress bar component.
        info_msg: UI info message component.
        start_time: Translation start time.
        lang_file_path: File being translated.

    Returns:
        Tuple of (translated_text, updated_count).

    Raises:
        TranslationError: If translation fails.
    """
    try:
        result = translate_text(client, text)
        translated_count += 1

        if page and progressbar and info_msg:
            from ..ui.components import update_progress_bar

            update_progress_bar(
                progressbar,
                translated_count,
                total_count,
                info_msg,
                page,
                start_time,
            )

        pbar.update(1)
        return result, translated_count
    except Exception as e:
        logger.error(f"Error translating {lang_file_path}: {e}", exc_info=True)
        raise TranslationError(f"Failed to translate {lang_file_path}") from e


def _translate_nested_dict(
    client,
    nested_dict,
    translated_count,
    total_count,
    pbar,
    page,
    progressbar,
    info_msg,
    start_time,
    lang_file_path,
):
    """Translate strings in a nested dictionary.

    Args:
        client: OpenAI client.
        nested_dict: Dictionary containing strings to translate.
        translated_count: Current count of translated strings.
        total_count: Total strings to translate.
        pbar: Progress bar object.
        page: UI page object.
        progressbar: UI progress bar component.
        info_msg: UI info message component.
        start_time: Translation start time.
        lang_file_path: File being translated.

    Returns:
        Tuple of (translated_dict, updated_count).

    Raises:
        TranslationError: If translation fails.
    """
    ja_dict = {}
    for sub_key, sub_value in nested_dict.items():
        if isinstance(sub_value, str):
            result, translated_count = _translate_and_update_progress(
                client,
                sub_value,
                translated_count,
                total_count,
                pbar,
                page,
                progressbar,
                info_msg,
                start_time,
                lang_file_path,
            )
            ja_dict[sub_key] = result
        else:
            ja_dict[sub_key] = sub_value
    return ja_dict, translated_count


def _save_translated_json(lang_file_path: str, ja_json: Dict) -> None:
    """Save translated JSON to file.

    Args:
        lang_file_path: Original file path.
        ja_json: Translated JSON data.
    """
    output_path = lang_file_path.replace("en_us.json", "ja_jp.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ja_json, f, indent=4, ensure_ascii=False)


def _finalize_progress(page, info_msg, translated_count: int, total_count: int) -> None:
    """Update final progress message.

    Args:
        page: UI page object.
        info_msg: UI info message component.
        translated_count: Number of translated strings.
        total_count: Total strings.
    """
    if page and info_msg:
        info_msg.value = f"完了：{translated_count}/{total_count}箇所を翻訳しました。"
        page.update()

def translate_all_files(lang_file_paths: List[str], page=None) -> bool:
    """Translate all language files in parallel.

    Args:
        lang_file_paths: List of paths to en_us.json files.
        page: The UI page object (optional).

    Returns:
        True if all translations were successful, False otherwise.

    Raises:
        TranslationError: If any translation fails.
    """
    if not lang_file_paths:
        logger.info("No files to translate.")
        return True

    try:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(translate_json_file, path, page)
                for path in lang_file_paths
            ]

            for future in futures:
                if not future.result():
                    logger.error("Translation failed for one or more files.")
                    return False

        logger.info("All translations completed successfully.")
        return True

    except Exception as e:
        logger.error(f"Error in translation process: {e}", exc_info=True)
        raise TranslationError("Failed to translate files") from e
