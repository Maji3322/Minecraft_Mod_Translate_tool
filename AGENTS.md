# AGENTS.md - AI Coding Agent Guide for Minecraft Mod Translate Tool

This document provides comprehensive guidance for AI coding agents working on the Minecraft Mod Translate Tool project.

## Project Overview

**Minecraft Mod Translate Tool** is a Python desktop application that translates Minecraft Java Edition MOD language files using OpenRouter LLM API. It creates resource packs with Japanese translations of MOD items and text.

**Tech Stack:**
- **Language**: Python 3.11+
- **GUI Framework**: Flet (cross-platform UI)
- **Translation**: OpenRouter API (346+ LLM models)
- **Build**: Nuitka (compilation to executable)

### Directory Structure

```
root/
├── src/
│   ├── core/          # Core business logic
│   │   ├── file_manager.py      # JAR extraction and file operations
│   │   ├── translator.py        # LLM translation with retry/fallback
│   │   ├── resource_pack.py     # Resource pack generation
│   │   └── openrouter_api.py    # OpenRouter API client
│   ├── ui/            # User interface
│   │   ├── app.py               # Main application class
│   │   ├── components.py        # Reusable UI components
│   │   └── styles.py            # UI themes and styling
│   ├── utils/         # Utilities
│   │   ├── config.py            # Configuration management
│   │   ├── logging.py           # Logging setup
│   │   └── exceptions.py        # Custom exceptions
│   └── main.py        # Application entry point
├── main.py            # Root entry point
├── resources/         # Application assets (icons, etc.)
├── requirements.txt   # Python dependencies
└── pyproject.toml     # Project metadata

## Coding Conventions

### Code Style (Recently Refactored - 2025-02)
- **Docstrings**: Google style format for all functions/classes
- **Constants**: Extracted to module top (uppercase names)
- **Type Hints**: Used throughout, especially for public APIs
- **Line Length**: Keep functions focused (<100 lines preferred)
- **Comments**: Minimal inline comments; let code self-document

### Key Patterns
- **Error Handling**: Use custom exception classes from `utils.exceptions`
- **Logging**: Use module-level logger via `logging.getLogger(__name__)`
- **Config Access**: Use global `config` instance from `utils.config`
- **UI State**: Store in `page.data` dictionary with helper `initialize_page_data()`

### Extracted Constants Examples
```python
# UI text constants at module top
TEXT_TRANSLATING = "翻訳中..."
TEXT_PROCESSING = "処理中..."

# UI sizing constants
DEFAULT_WINDOW_WIDTH = 1000
PROGRESS_BAR_WIDTH = 300

# Translation constants
TRANSLATION_SYSTEM_PROMPT = "You are a professional translator..."
```

## File Organization
- Each module has single responsibility
- Complex functions decomposed into helpers (private `_` prefix)
- Constants extracted to reduce duplication
- Helper functions near usage, or at module top if shared

## State Management
- Application state in `MinecraftModTranslatorApp` class
- UI state in `page.data` dictionary
- Configuration in global `config` singleton
- OpenRouter client cached for connection pooling

## Development Commands

**No automated linting/testing configured** - manual verification required

### Running the Application
```bash
# From repository root
python main.py

# Or from src directory  
python -m src.main
```

### Syntax Validation
```bash
python -m py_compile src/**/*.py main.py
```

### Manual Testing
1. Select Minecraft version
2. Choose JAR file(s) or paste mods folder path
3. Verify translation progress
4. Check `translate_rp/` output directory

## Common Issues

### Translation Errors
- **"API key not set"**: OpenRouter API key not configured in settings
- **"Rate limit"**: Switch to fallback model or use different model
- **"No translatable files"**: MOD doesn't have language files

### File Operations
- Ensure write permissions to temp/ and translate_rp/ directories
- JAR files must contain assets/*/lang/en_us.json structure

## Performance Considerations
- Parallel translation of multiple MODs using ThreadPoolExecutor
- OpenAI client reuse for connection pooling
- Progress bars for long-running operations
- Nested JAR extraction cached in temp directory

## Debugging Tips
- Check `logs/mcmt.log` for detailed error traces
- Use `logger.debug()` for detailed flow information
- UI errors logged with full stack traces

## Recent Refactoring (2025-02)

The codebase underwent comprehensive refactoring:

1. **Standardized Docstrings**: All modules use Google-style format
2. **Extracted Constants**: Magic strings/numbers moved to module constants
3. **Decomposed Functions**: Large functions (>100 lines) split into helpers
4. **Removed Duplication**: DRY principle applied across UI and core modules
5. **Improved Readability**: Comments removed where code is self-documenting

**Affected Files** (12 files, ~1000 lines refactored):
- `src/core/*`: translator.py, file_manager.py, openrouter_api.py
- `src/ui/*`: app.py, components.py, styles.py  
- `src/utils/*`: config.py, logging.py, exceptions.py
- `src/main.py`, `main.py`

## Contributing Guidelines

### Before Making Changes
1. Review existing code patterns
2. Maintain consistency with refactored style
3. Keep changes minimal and focused
4. Verify all Python files compile

### Making Changes
1. Follow Google-style docstrings
2. Extract magic values to constants
3. Decompose functions >80 lines
4. Use existing exception classes
5. Manual test before committing

### Pull Requests
- Describe changes clearly
- Reference related issues
- Include manual test results
- Ensure syntax validation passes

## MCP Servers
Use provided MCP servers actively for enhanced development capabilities.

---

Last Updated: 2025-02 (Post-Refactoring)
Maintained for AI coding agents. Keep updated as project evolves.
