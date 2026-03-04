---
name: openrouter-translation-maintenance
description: Maintain and evolve this repository's OpenRouter-based translation pipeline. Use when tasks involve translation behavior changes, OpenRouter model fetch/search and settings UI, API key/model/fallback configuration handling, rate-limit and auth error handling, or migration/documentation updates for LLM translation workflows.
---

# OpenRouter Translation Maintenance

## Overview

Use this skill to implement or review changes around the OpenRouter translation flow, from settings UI to runtime translation calls.
Apply this skill when touching `src/core/translator.py`, `src/core/openrouter_api.py`, `src/ui/components.py`, or `src/utils/config.py`.

## Route the Task

- If the request changes translation quality, prompt design, retry logic, or fallback behavior:
  - Edit `src/core/translator.py`.
  - Follow `references/workflows.md` section "Translation Runtime Changes".
- If the request changes model discovery, filtering, or model selection UX:
  - Edit `src/core/openrouter_api.py` and `src/ui/components.py`.
  - Follow `references/workflows.md` section "Model Discovery and Settings UI".
- If the request changes API key/model/fallback storage rules:
  - Edit `src/utils/config.py` and UI save logic in `src/ui/components.py`.
  - Follow `references/workflows.md` section "Configuration and State Rules".
- If the request changes user instructions:
  - Update repo docs and keep guidance aligned with the actual UI flow.

## Keep These Invariants

- Validate API key before creating an OpenRouter client.
- Reuse one shared OpenAI client for connection pooling.
- Reset cached client when API key changes.
- Try primary model first, then `FALLBACK_MODELS` in order.
- Treat rate-limit/payment errors as fallback-eligible.
- Fail fast on authentication errors.
- Require both API key and primary model before saving settings.
- Keep API key in memory unless explicit persistence is requested.

## Execution Checklist

1. Map the request to the matching workflow in `references/workflows.md`.
2. Keep changes minimal and localized to relevant modules.
3. Verify behavior against `references/current-architecture.md`.
4. Run checks from `references/change-checklist.md`.
5. Update user-facing docs when behavior or setup changes.

## Resources

- `references/current-architecture.md`
- `references/workflows.md`
- `references/change-checklist.md`
