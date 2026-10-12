# Autoweb testing framework

A Python framework for reusable Playwright login tests, with an independent Gmail verification module. Phases I and II establish packaging, validated configuration, and async browser primitives. Complete login flows and Gmail integration will be implemented in subsequent phases described in [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

## Environment and installation

Use the existing conda environment **autoweb** for all project commands. Run installation commands from the repository root:

~~~powershell
conda run -n autoweb python -m pip install -e ".[test]"
~~~

Gmail and Gemini dependencies are optional for the new package:

~~~powershell
conda run -n autoweb python -m pip install -e ".[gmail,ai,test]"
~~~

Dependencies are declared in pyproject.toml. Versions reflect the installed autoweb baseline verified during Phase I (Python 3.10.18), rather than an SDK upgrade. The legacy requirements files delegate to this definition and must also be used from the repository root. Install the matching Chromium binary for browser integration tests:

~~~powershell
conda run -n autoweb python -m playwright install chromium
~~~

## Structure

| Location | Responsibility |
| --- | --- |
| src/autoweb/config/ | Settings, typed site profiles, credential preflight, validation CLI |
| src/autoweb/browser/ | Async Playwright lifecycle, strict locator resolution, actions, and state waits |
| src/autoweb/gmail/ | Future independent email verification implementation |
| src/autoweb/login/ | Future login flow and authenticated-session handoff |
| src/autoweb/ai/ | Future optional AI adapters |
| src/autoweb/reporting/ | Future step results and failure diagnostics |
| configs/settings.json | Non-secret browser, timeout, mailbox-path, and AI defaults |
| configs/sites/ | Non-secret example site profiles |
| tests/unit/ | Configuration and browser failure-path tests |
| tests/integration/ | Real headless Chromium checks against controlled local pages |
| tests/fixtures/ | Ordinary DOM, open Shadow DOM, and nested iframe fixtures |
| scripts/ | Future thin execution and Gmail diagnostic entry points |
| artifacts/ | Ignored runtime output; created by future execution code as needed |

Gmail, login, AI, and reporting packages currently define future boundaries. The browser package implements reusable primitives; see its [API and ownership documentation](src/autoweb/browser/README.md). Importing the new package does not open a browser, authenticate with Gmail, load a dotenv file, or create an AI client. Configuration loading is explicit.

## Check configuration

The example profiles target example.com and illustrate the schema; they are not runnable login tests. Check a profile without supplying credentials:

~~~powershell
conda run -n autoweb python -m autoweb.config --site configs/sites/password.example.json --schema-only
~~~

Copy .env.example to .env at the repository root and supply test-account values to check credential references as well:

~~~powershell
conda run -n autoweb python -m autoweb.config --site configs/sites/password.example.json
~~~

The equivalent installed command is autoweb-config. Invalid configuration exits with status 2. Schema-only mode skips secret resolution and is not a readiness check for login. Neither mode makes Gmail, Gemini, or browser calls; OAuth-file validity belongs to the later Gmail phase; browser availability is exercised by the Phase II integration tests.

The configuration API is load_configuration, load_settings, and load_site_profile from autoweb.config. load_configuration performs credential preflight by default and returns settings, the typed site profile, and masked SecretStr values under keys such as credential:password and verification:recipient. Secrets are omitted from the configuration representation. Execution code must explicitly access a secret when filling a field and must not log it.

## Paths and environment precedence

- Relative site, settings, dotenv, OAuth, and artifact paths resolve against the repository root, independently of the working directory.
- The editable installation discovers this root from its package location. Set AUTOWEB_ROOT or pass --project-root for another configuration root, including a non-editable installation.
- Defaults come from configs/settings.json. The root .env supplies overrides and credentials; process environment variables take precedence.
- Use --env-file to select another dotenv file explicitly. Existing .env files inside the legacy projects are not automatically merged.
- Loading dotenv values does not mutate the process environment or interpolate other variables.
- Original Gmail credential/token files remain in gmail-auto/. Override their paths without moving the files.

See [configs/README.md](configs/README.md) for the schema and environment overrides. Credentials, OAuth files, generated artifacts, and session state are ignored by Git.

## Tests

~~~powershell
conda run -n autoweb python -m pytest -q
~~~

Tests cover profile validation, credential resolution, secret-safe output, paths, import isolation, browser lifecycle, scoped locators, nested iframes, open Shadow DOM, password/OTP filling, explicit failures, and state waits. Browser integration tests use a loopback HTTP server and headless Chromium. They do not use live websites or Gmail/Gemini access.

## Existing projects

The original gmail-auto/ and shadowdom-auto/ projects remain available while their behavior is migrated incrementally. Their existing entry points are legacy demonstrations and do not use the new profile schema or preflight API yet. The new configuration checker does not validate or execute their old JSON formats. The historical browser demo fills an identifier, not a complete password/OTP login.

trial-codes/ is excluded from active development and context.

The original [demo videos](https://drive.google.com/drive/folders/1un7WF-h4Xu3I62vAHyjiQSVvcZET6SKU?usp=sharing) document the earlier standalone projects.
