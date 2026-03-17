"""Ollama API integration for checking server status and available models."""

import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


def candidate_ollama_base_urls(base_url: str) -> list[str]:
    """Return preferred Ollama base URLs to try for a configured endpoint.

    On Windows, resolving ``localhost`` can trigger Wi-Fi scanning via the OS
    network-location service, which causes spurious location permission requests.
    When the configured URL uses ``localhost``, ``127.0.0.1`` is tried first so
    that DNS resolution is skipped entirely.  ``localhost`` is kept as a fallback
    for environments where only that name is routed correctly.
    """
    normalized = base_url.rstrip("/")

    if "://localhost" in normalized:
        # Try 127.0.0.1 first to avoid DNS resolution of "localhost".
        # On Windows, resolving "localhost" can trigger Wi-Fi scanning via the
        # OS network-location service, which causes spurious location permission
        # requests. Using the literal IPv4 loopback address bypasses that lookup.
        ipv4_url = normalized.replace("://localhost", "://127.0.0.1", 1)
        urls = [ipv4_url, normalized]
    else:
        urls = [normalized]

    return list(dict.fromkeys(urls))


def resolve_ollama_base_url(base_url: str) -> str:
    """Return a reachable Ollama base URL, falling back to IPv4 localhost.

    If none of the candidates respond, the original URL is returned so the
    eventual translation error still reflects the configured endpoint.
    """
    original = base_url.rstrip("/")

    for url in candidate_ollama_base_urls(base_url):
        try:
            response = httpx.get(f"{url}/api/tags", timeout=3)
            if response.status_code == 200:
                if url != original:
                    logger.info(
                        "Resolved Ollama base URL from %s to %s for runtime requests",
                        original,
                        url,
                    )
                return url
        except Exception as e:
            logger.debug(
                "Ollama base URL candidate %s was not reachable during resolution: %s: %s",
                url,
                type(e).__name__,
                e,
            )

    return original


def check_ollama_running(base_url: str) -> tuple[bool, Optional[dict]]:
    """Check if Ollama server is running by querying /api/tags.

    Args:
        base_url: Ollama server base URL (e.g., 'http://localhost:11434').

    Returns:
        Tuple of (is_running, tags_data). tags_data is None if not running.
    """
    for url in candidate_ollama_base_urls(base_url):
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
