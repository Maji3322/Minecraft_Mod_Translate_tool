"""Ollama API integration for checking server status and available models."""

import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


def check_ollama_running(base_url: str) -> tuple[bool, Optional[dict]]:
    """Check if Ollama server is running by querying /api/tags.

    Args:
        base_url: Ollama server base URL (e.g., 'http://localhost:11434').

    Returns:
        Tuple of (is_running, tags_data). tags_data is None if not running.
    """
    # On Windows, 'localhost' may resolve to IPv6 (::1) which Ollama doesn't
    # listen on by default. Fall back to 127.0.0.1 if the primary URL fails.
    urls_to_try = [base_url]
    if "localhost" in base_url:
        urls_to_try.append(base_url.replace("localhost", "127.0.0.1"))

    for url in urls_to_try:
        try:
            logger.info(f"Connecting to Ollama: GET {url}/api/tags")
            t0 = time.time()
            response = httpx.get(f"{url}/api/tags", timeout=3)
            elapsed_ms = (time.time() - t0) * 1000
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                logger.info(
                    f"Ollama responded in {elapsed_ms:.0f}ms. "
                    f"Available models ({len(models)}): {models or '(none)'}"
                )
                return True, data
            logger.warning(
                f"Ollama at {url} returned HTTP {response.status_code} "
                f"in {elapsed_ms:.0f}ms"
            )
        except Exception as e:
            logger.warning(f"Ollama not reachable at {url}: {type(e).__name__}: {e}")

    return False, None


def check_model_downloaded(tags_data: dict, model_name: str) -> bool:
    """Check if a specific model is available in the local Ollama installation.

    Args:
        tags_data: Response data from /api/tags.
        model_name: Model name to check (e.g., 'mitmul/plamo-2-translate').

    Returns:
        True if the model is available locally.
    """
    models = tags_data.get("models", [])
    available_names = [m.get("name", "") for m in models]
    for name in available_names:
        # Ollama model names can include tags like "mitmul/plamo-2-translate:latest"
        if name == model_name or name.startswith(f"{model_name}:"):
            logger.info(f"Model '{model_name}' found: {name}")
            return True
    logger.warning(
        f"Model '{model_name}' not found. "
        f"Available: {available_names or '(none)'}"
    )
    return False


def list_local_models(base_url: str) -> list[str]:
    """Get list of locally available model names.

    Args:
        base_url: Ollama server base URL.

    Returns:
        List of model name strings.
    """
    is_running, tags_data = check_ollama_running(base_url)
    if not is_running or tags_data is None:
        return []
    return [m.get("name", "") for m in tags_data.get("models", []) if m.get("name")]
