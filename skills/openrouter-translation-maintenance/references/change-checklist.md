# Change Checklist

## Code Checks

- `src/core/translator.py` still validates API key before client creation.
- Shared OpenRouter client is still reused.
- API key change path still calls `reset_openrouter_client`.
- Fallback order is deterministic (configured order).
- Auth errors are still handled as immediate failures.
- Rate-limit/payment errors still trigger fallback attempts.

## UI Checks

- Settings dialog rejects empty API key.
- Settings dialog rejects missing primary model.
- Model fetch and search still function.
- Fallback add/remove controls still function.

## Verification Commands

```bash
python -m compileall src
```

Run app manually when feasible:

```bash
python main.py
```

Then verify:

- Save settings with valid API key and selected model.
- Trigger translation once with no fallback and once with fallback configured.

## Documentation Checks

- Keep `README.md` and relevant docs aligned with current settings flow.
- Avoid stale references to removed translators or old setup steps.
