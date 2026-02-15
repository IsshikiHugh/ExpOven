# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ExpOven is a Python notification utility for AI researchers. It monitors experiments and sends notifications to various messaging platforms via a pluggable backend system. It provides both CLI tools (`bake`, `ding`, `oven`) and a Python package API (`import oven`).

## Commands

### Installation
```bash
pip install .
```

### Formatting (enforced in CI)
```bash
blue $(git ls-files '*.py') --check   # check only
blue .                                 # auto-format
```
The project uses **Blue** (not Black) as its formatter. CI runs the check on every push across Python 3.8, 3.9, 3.10.

### Testing
Unit tests (no config needed):
```bash
python -m unittest discover tests/ -p 'test_*.py' -v
```
Integration tests (in `tests/integration/`, may need config):
```bash
python tests/integration/pbar.py
python tests/integration/error_handling.py
```

## Architecture

### Backend Plugin System

```
User Code (CLI / Python API)
    → Oven (core orchestrator)
        → NotifierBackendBase (abstract interface)
            → Concrete backends (DingTalk, Feishu, Slack, Email, ...)
                → Third-party APIs
```

- **`oven/oven.py`** — `Oven` class: central coordinator. `build_oven()` factory loads YAML config and creates an instance. `_init_notifier()` dynamically imports the selected backend.
- **`oven/backends/api/info.py`** — Defines the Signal system (`I/S/P/T/E`) and base classes `ExpInfoBase` (long-running experiments with multiple signals) and `LogInfoBase` (single messages).
- **`oven/backends/<name>/`** — Each backend provides three classes: `*Backend(NotifierBackendBase)`, `*ExpInfo(ExpInfoBase)`, `*LogInfo(LogInfoBase)`. Add new backends by following this pattern.
- **`oven/__init__.py`** — Public API with lazy global oven instance. Exports `bake`/`monitor`, `ding`/`notify`, `progress`, `ProgressBar`.
- **`oven/cli.py`** — CLI handlers for the three entry points defined in `setup.py`.
- **`oven/progress.py`** — tqdm-like `ProgressBar` with optional notification integration (HTTP polling or socket-triggered modes).

### Signal Lifecycle

`ExpInfoBase` tracks experiment state via signals: `I` (init) → `S` (start) → `P` (progress, repeated) → `T` (terminate) or `E` (exception). Each signal transition calls `custom_signal_handler()` then `backend.notify()`.

### Configuration

YAML config at `$OVEN_HOME/cfg.yaml` (default `~/.config/oven/cfg.yaml`), managed via OmegaConf. The `backend` field selects the active backend; remaining keys hold backend-specific settings.

## Key Conventions

- Python >= 3.8 compatibility required
- Type hints on all public methods
- `# fmt: off/on` for intentionally unformatted blocks (e.g., emoji pools)
- DingTalk backend is the reference implementation for new backends
- **Always run `blue` on changed files before committing** to ensure formatting compliance. Run automatically without asking.
- **Always run unit tests (`python -m unittest discover tests/ -p 'test_*.py'`) before committing** to verify changes don't break existing functionality. Run automatically without asking.
- **Use the conda `cv` environment** for running tests and formatting: `eval "$(/opt/miniconda3/condabin/conda shell.bash hook)" && conda activate cv`
- **Bump the version in `oven/version.py` when making changes.** Follow semver: patch for bug fixes and non-functional changes (tests, refactors), minor for new features or enhancements, major for breaking changes. Bump wisely — if a change is logically part of an already-bumped change (e.g., adding CI for tests that were already versioned), don't bump again
- **Always ask the user before pushing to remote**
- **Never write sensitive information** (API keys, tokens, passwords, webhook URLs, personal paths, etc.) into any tracked file, including this one. Use placeholders (e.g., `<?>`) in examples. Config files containing secrets (`cfg.yaml`) are already gitignored
