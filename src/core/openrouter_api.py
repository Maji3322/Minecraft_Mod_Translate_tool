"""OpenRouter API integration for fetching models and handling rate limits."""

import logging
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class OpenRouterAPI:
    """Client for interacting with OpenRouter API."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenRouter API client.

        Args:
            api_key: Optional API key for authenticated requests.
        """
        self.api_key = api_key

    def fetch_models(self) -> List[Dict]:
        """Fetch available models from OpenRouter API.

        Returns:
            List of model dictionaries with id, name, pricing, etc.

        Raises:
            Exception: If API request fails.
        """
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.get(
                f"{self.BASE_URL}/models", headers=headers, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            models = data.get("data", [])

            logger.info(f"Fetched {len(models)} models from OpenRouter")
            return models

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch models from OpenRouter: {e}")
            raise Exception(f"モデルの取得に失敗しました: {str(e)}") from e

    def search_models(self, models: List[Dict], search_term: str) -> List[Dict]:
        """Search models by partial name match.

        Args:
            models: List of model dictionaries.
            search_term: Search term for partial matching.

        Returns:
            List of matching models.
        """
        if not search_term:
            return models

        search_lower = search_term.lower()
        matching_models = []

        for model in models:
            model_id = model.get("id", "").lower()
            model_name = model.get("name", "").lower()

            if search_lower in model_id or search_lower in model_name:
                matching_models.append(model)

        return matching_models

    def format_model_info(self, model: Dict) -> str:
        """Format model information for display.

        Args:
            model: Model dictionary.

        Returns:
            Formatted string with model info.
        """
        model_id = model.get("id", "Unknown")
        model_name = model.get("name", "Unknown")
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", "0")
        completion_price = pricing.get("completion", "0")

        is_free = str(prompt_price) == "0" and str(completion_price) == "0"
        free_tag = " [無料]" if is_free else ""

        return f"{model_name}{free_tag}\n  ID: {model_id}"

    @staticmethod
    def is_rate_limit_error(error: Exception) -> bool:
        """Check if an error is a rate limit error.

        Args:
            error: Exception to check.

        Returns:
            True if error is rate limit related.
        """
        error_str = str(error).lower()
        return (
            "429" in error_str
            or "402" in error_str
            or "rate limit" in error_str
            or "too many requests" in error_str
            or "payment required" in error_str
        )
