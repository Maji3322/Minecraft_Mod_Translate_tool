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
AGENTS.md
...

```

## Agent Skills
Please make appropriate and active use of any existing items in the list below.
If a skill does not exist and is deemed necessary, please read the instructions for the "Skill Creator" tool (https://raw.githubusercontent.com/anthropics/skills/refs/heads/main/skills/skill-creator/SKILL.md) and create it.

- Key Modules
- Prerequisites
- Coding Conventions
- File Naming
- Code Organization
- State Management
- Environment Variables
- Performance Considerations
- Debugging Tips
- Common Issues
- Development Tools
- Contributing Guidelines
- Development Commands

## MCP Servers
Use provided MCP servers actively. It provides really useful features. Do not forget to use in a appropriate situation. 

### Before Starting Work
1. Review existing code for patterns and conventions
2. Check for related issues or PRs
3. Understand the affected components and their dependencies

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
