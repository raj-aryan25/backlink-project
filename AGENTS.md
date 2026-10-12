# Agent instructions

## Project environment

- Use the conda environment `autoweb` for running project commands, scripts, dependency operations, and tests. Prefer `conda run -n autoweb <command>` or activate `autoweb` before running commands. Do not use another Python environment implicitly.

## Project scope

- `gmail-auto/` contains the Gmail verification-code automation project.
- `shadowdom-auto/` contains the Playwright-based website automation project.
- Ignore `trial-codes/` (also referred to as "trial codes"). It contains historical experiments and is not relevant to future analysis or implementation. Do not treat it as a source of requirements or production code.
- The intended direction is a unified framework for end-to-end website login, combining browser automation with email verification retrieval.

## Code design

- Keep code clean, readable, and modular.
- Use focused functions and modules for distinct tasks, with clear responsibilities and interfaces.
- Separate login orchestration, browser/session management, UI interaction, email access, verification extraction, and configuration.
- Prefer reusable components over duplicated or hardcoded site-specific flows.

## Current authorization

- The user has authorized Phase II (reliable Playwright browser primitives) of IMPLEMENTATION_PLAN.md. Keep implementation within that phase until the user requests a subsequent phase.
- Active framework code lives in src/autoweb/. The original projects remain legacy implementations until their corresponding migration phases.
- Use pyproject.toml as the single dependency definition. Avoid browser, Gmail, or AI client initialization during package imports.
