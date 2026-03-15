# Workflows

## Translation Runtime Changes

Use this when changing prompt wording, retries, fallback order, or response cleanup.

1. Edit `src/core/translator.py`.
2. Preserve model order: primary first, then `FALLBACK_MODELS`.
3. Keep auth failures non-retryable and fallback-agnostic.
4. Keep rate-limit/payment failures fallback-eligible.
5. Preserve response cleanup for formatting-sensitive strings.
6. Run checklist in `change-checklist.md`.

## Model Discovery and Settings UI

Use this when changing model fetch/search/select behavior.

1. Edit `src/core/openrouter_api.py` for fetch/filter rules.
2. Edit `src/ui/components.py` for dialog behavior.
3. Keep partial-match search on model id/name.
4. Keep free/paid labeling consistent with pricing fields.
5. Keep explicit validation for API key and selected model before save.
6. Verify fallback add/remove behavior still works.

## Configuration and State Rules

Use this when changing config fields or persistence semantics.

1. Edit `src/utils/config.py`.
2. Keep API key in memory by default.
3. Keep `OPENROUTER_MODEL` and `FALLBACK_MODELS` runtime-editable.
4. If API key lifecycle changes, keep `reset_openrouter_client` integration correct.
5. If adding persistence, update docs and security notes in the same change.

## Documentation Update Scope

Update user docs when any of these changes:

- Setup steps (API key, model selection, fallback configuration)
- Required environment variables or defaults
- Error/recovery behavior visible to users
- Supported model guidance or recommendations
