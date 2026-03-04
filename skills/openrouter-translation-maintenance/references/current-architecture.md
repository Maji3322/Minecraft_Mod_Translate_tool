# Current Architecture

## Modules and Responsibilities

- `src/core/translator.py`
  - Build and cache OpenRouter client (`get_openrouter_client`).
  - Reset cache on API key change (`reset_openrouter_client`).
  - Execute translation with prompt, retry, and fallback model flow.
  - Categorize errors (rate-limit/payment/auth/other).
- `src/core/openrouter_api.py`
  - Fetch available models from `https://openrouter.ai/api/v1/models`.
  - Filter models by partial match in id/name.
  - Format model labels and free/paid tagging.
- `src/ui/components.py`
  - Render OpenRouter settings dialog.
  - Fetch model list, search models, choose primary model.
  - Manage fallback model list.
  - Save API key/model/fallbacks and reset cached client when key changes.
- `src/utils/config.py`
  - Hold runtime OpenRouter state:
    - `OPENROUTER_API_KEY`
    - `OPENROUTER_MODEL`
    - `FALLBACK_MODELS`
  - Keep API key in memory (initialized from env if present).

## Runtime Flow

1. User opens settings dialog and enters API key.
2. UI fetches model list and user selects primary model.
3. UI optionally adds ordered fallback models.
4. On save, config updates runtime values.
5. If API key changed, translator client cache resets.
6. Translation request uses primary model first, then fallbacks as needed.

## Error Handling Expectations

- Retry with backoff for transient errors through decorator.
- Switch model on rate-limit/payment-style failures.
- Stop immediately on auth/API-key failures.
- Raise clear `TranslationError` when all models fail.
