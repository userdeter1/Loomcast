# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Model lifecycle management: `remove` and `update` commands and SDK functions.
- `doctor` command running diagnostics across configuration, environment
  variables, runtime availability, catalog reachability, and static catalog
  integrity.
- `loomcast.__version__`, read from installed package metadata.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, and GitHub issue templates.
- Project URLs in package metadata, so PyPI links back to the repository.

### Fixed
- Dynamic catalog parsing captured listing-page furniture as model tags. Every
  scraped entry carried pull counters, tag counts, update dates, and undecoded
  `&nbsp;` entities, which made tag search match every model in the catalog
  (`search("ago")` returned all 233 entries). Tags are now read only from tag
  pill elements, and HTML entities are decoded.
- Model descriptions could pick up the stats footer instead of the description
  text, and kept raw HTML entities.
- The dynamic catalog cache key is bumped to `_v2`, so snapshots written by
  earlier versions are ignored rather than served for up to 24 hours after
  upgrading.
- `config` displayed `RuntimeType.OLLAMA` instead of the `ollama` value that
  `--set-default-backend` accepts.
- CLI help omitted llama.cpp from the list of supported runtimes.

### Changed
- User-facing output in `doctor`, `update`, `remove`, and `verify` is now in
  English, matching the rest of the CLI.
- The whole project is now in English: `CONTRIBUTING.md`, all five `docs/`
  guides, the pull request template, the integration test comments, and the
  Gitleaks config were translated from French.
- `--backend` and `--set-default` help text now lists `llamacpp`, which was
  supported but undocumented.
- `docs/extending.md` documented a `RuntimePort` missing `remove()` and
  `update()`; it now matches the actual protocol.
- Ruff is pinned to 0.16.0 and the lint rule set is declared explicitly via
  `select`. Previously only `ignore` was set, so ruff fell back to its built-in
  defaults, which changed between releases and broke CI.

## [0.1.1] - 2026-07-23

### Fixed
- The static catalog file was missing from the published package, which made
  almost every command unusable after a normal install from PyPI.

## [0.1.0] - 2026-07-22

### Added
- **Local LLM Runtime Adapters**: Support for local runtimes:
  - Ollama (`OllamaRuntime`) via HTTP API on port 11434.
  - LM Studio (`LMStudioRuntime`) via OpenAI-compatible endpoint on port 1234.
  - llama.cpp (`LlamaCppRuntime`) via `llama-server` on port 8080.
- **Shared OpenAI Compatibility**: Refactored shared OpenAI-compatible chat response parsing (`send_openai_compat_chat`).
- **Download Progress Tracking**:
  - `ProgressReporter` base callback interface.
  - `RichProgressReporter` for visual terminal progress bars using `rich.progress` (`Progress`, `BarColumn`, `DownloadColumn`, `TransferSpeedColumn`).
  - `NullProgressReporter` for silent execution in SDK and test environments.
  - `SubProgressReporter` for per-task isolated progress reporting in parallel executions.
  - Streaming NDJSON response parsing in `OllamaRuntime.install()`.
- **Parallel Category Installation**:
  - Parallelized `loomcast.install_category()` using `concurrent.futures.ThreadPoolExecutor`.
  - Configurable concurrency level (`max_concurrent: int = 3`).
  - CLI flags `--max-concurrent` (`-c`) and `--sequential` (`-s`).
  - Fault-tolerant execution where individual model installation failures do not interrupt other concurrent downloads.
- **Environment Variable Overrides**:
  - Priority hierarchy: `Environment Variables > config.toml > Pydantic Defaults`.
  - Supported environment variables: `LOOMCAST_DEFAULT_BACKEND`, `LOOMCAST_OLLAMA_URL`, `LOOMCAST_LMSTUDIO_URL`, `LOOMCAST_LLAMACPP_URL`, and `LOOMCAST_CATALOG_SOURCE`.
  - Strict Pydantic validation with explicit `ConfigurationError` messages.
  - Non-persistence policy preventing environment overrides from being saved to `config.toml`.
- **Catalog & Caching**:
  - Content-addressed `FileSystemCache` for local catalog caching.
  - `DynamicCatalog` with scraping and fallback to `StaticCatalog`.
- **Verification System**:
  - `ModelVerifier` and `loomcast verify` command to check installed model integrity against digest signatures.
- **CLI & SDK**:
  - Full CLI built with Typer and Rich (`status`, `list`, `search`, `recommend`, `install`, `install-category`, `chat`, `verify`, `config`).
  - Python SDK interface exposed via top-level `loomcast` module functions.
