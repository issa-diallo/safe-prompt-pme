# Repository Guidelines

## Project Structure & Module Organization

This is a Python package using a `src/` layout. Core code lives in
`src/safe_prompt_pme/`: `anonymizer.py` handles sensitive-data masking,
`llm.py` contains LLM client abstractions, `demo.py` provides demo workflow
helpers, `interfaces.py` defines shared contracts, `constants.py` centralizes
tokens and patterns, and `app.py` contains the Streamlit UI. Tests live in
`tests/` with one focused file per module or workflow. Product and explanatory
documentation lives under `docs/`.

## Build, Test, and Development Commands

Create a local environment before installing dependencies:

```bash
uv venv
.venv/bin/pip install -e ".[dev]"
```

Run the local app with:

```bash
.venv/bin/streamlit run src/safe_prompt_pme/app.py
```

Quality checks:

```bash
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/mypy src
```

`pytest` enforces coverage through `pyproject.toml`; `ruff` checks style,
imports, and common bug patterns; `mypy` runs in strict mode.

## Coding Style & Naming Conventions

Target Python 3.11+ and keep lines at or below 88 characters. Prefer pure
functions for business logic, explicit interfaces, and small modules with clear
responsibilities. Keep constants and token patterns in `constants.py`, shared
contracts in `interfaces.py`, and UI-only behavior in `app.py`. Sensitive-data
tokens should follow `[TYPE_1]`, `[TYPE_2]`, for example `[EMAIL_1]` or
`[MONTANT_1]`.

## Testing Guidelines

Every behavior in business logic needs an associated test. Add or update tests
before changing implementation when practical, then verify the test fails for
the missing behavior. Name tests by behavior, such as
`test_anonymizes_french_phone_numbers`. Keep fixtures synthetic: do not include
real customer data, API keys, emails, IBANs, or CRM exports. The configured
coverage threshold is 95%.

## Commit & Pull Request Guidelines

Use Conventional Commits, matching the existing history and `CONTRIBUTING.md`:
`feat: ...`, `fix: ...`, `docs: ...`, or `test: ...`. Branch names should use
the same prefixes, such as `feat/streamlit-provider`.

Pull requests should describe the user-visible change, list the checks run
(`pytest`, `ruff check .`, `mypy src`), link related issues when available, and
include screenshots for Streamlit UI changes.

## Security & Configuration Tips

Do not commit secrets or real business data. Keep API keys user-provided and
session-scoped, and prefer local anonymization before any external LLM call.
When adding providers or integrations, preserve the rule that validation and
reinjection of real values happen locally.
