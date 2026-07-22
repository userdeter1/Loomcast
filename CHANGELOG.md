# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-23

### Fixed
- Le fichier de catalogue statique n'était pas inclus dans le package publié, rendant presque toutes les commandes inutilisables après une installation normale depuis PyPI.

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
