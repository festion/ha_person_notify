# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure
- Home Assistant custom component for person notifications
- Located in `custom_components/person_notify/`
- Add-on in `addon/` for enhanced notification routing

## Build & Test Commands
- Run tests: `pytest tests/`
- Run single test: `pytest tests/test_file.py::test_function -v`
- Validate code: `hass-cli core check`
- Install in development mode: `pip install -e .`

## Code Style Guidelines
- Follow Home Assistant style guide: PEP8 with 4 spaces indentation
- Type hints required for all functions
- Import order: standard lib, third-party, home assistant, local modules
- Prefix constants with CONST_
- Use snake_case for variables and functions
- Class naming: PascalCase
- Error handling: use proper exception types with descriptive messages
- DocStrings: use Google style docstrings for all public methods