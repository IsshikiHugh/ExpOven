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

- **`oven/oven.py`** — `Oven` class: central coordinator. `build_oven()` factory loads group YAML config and creates an instance. Supports notification groups via `_load_group_config()`.
- **`oven/backends/registry.py`** — Backend registry: maps type strings to `(BackendClass, ExpInfoClass, LogInfoClass)` tuples with lazy imports. Register new backends here.
- **`oven/backends/api/__init__.py`** — `NotifierBackendBase(ABC)` with `@abstractmethod` for `notify()` and `get_meta()`. Also exports `RespStatus`.
- **`oven/backends/api/info.py`** — `Signal(IntEnum)` for signal values (`U/I/S/P/T/E`), base classes `ExpInfoBase` and `LogInfoBase`, and shared utilities `lines2reply()` / `plain2md()` used by DingTalk and Feishu backends.
- **`oven/backends/<name>/`** — Each backend provides three classes: `*Backend(NotifierBackendBase)`, `*ExpInfo(ExpInfoBase)`, `*LogInfo(LogInfoBase)`. Email backend uses HTML formatting; others use markdown. Slack keeps its own `lines2reply()` for platform-specific quoting.
- **`oven/__init__.py`** — Public API with lazy global oven instance. Exports `bake`/`monitor`, `ding`/`notify`, `toggle_ogroup`, `progress`, `progress_range`, `ProgressBar`, `get_lazy_oven`, `Oven`, `build_oven`.
- **`oven/cli.py`** — CLI handlers for the three entry points defined in `setup.py`.
- **`oven/progress.py`** — tqdm-like `ProgressBar` with optional notification integration (HTTP polling or socket-triggered modes).
- **`setup.py`** — Uses regex to parse version from `oven/version.py` (not `exec()`).

### Signal Lifecycle

`ExpInfoBase` tracks experiment state via signals: `I` (init) → `S` (start) → `P` (progress, repeated) → `T` (terminate) or `E` (exception). Each signal transition calls `custom_signal_handler()` then `backend.notify()`.

### Configuration

Config lives under `$OVEN_HOME` (default `~/.config/oven/`), managed via OmegaConf:

```
~/.config/oven/
├── config.yaml          # meta config: `default: <group_name>`
└── ogroups/
    ├── default.yaml     # default notification group
    └── <name>.yaml      # additional groups
```

Each group YAML contains a `backends` list — one entry per backend (type + credentials). Multiple backends in one group enable fan-out notifications. CLI commands: `oven init-cfg`, `oven set-default <group>`, `oven list-ogroups`. Python API: `oven.toggle_ogroup('group_name')` switches group at runtime.

## Key Conventions

- Python >= 3.8 compatibility required
- Type hints on all public methods
- `# fmt: off/on` for intentionally unformatted blocks (e.g., emoji pools)
- DingTalk backend is the reference implementation for new backends
- **Always run `blue` on changed files before committing** to ensure formatting compliance. Run automatically without asking.
- **Always run unit tests (`python -m unittest discover tests/ -p 'test_*.py'`) before committing** to verify changes don't break existing functionality. Run automatically without asking.
- **Use the conda `cv` environment** for running tests and formatting: `eval "$(/opt/miniconda3/condabin/conda shell.bash hook)" && conda activate cv`
- **Bump the version in `oven/version.py` when making changes.** Follow semver: patch for bug fixes and non-functional changes (tests, refactors), minor for new features or enhancements, major for breaking changes. Bump wisely — if a change is logically part of an already-bumped change (e.g., adding CI for tests that were already versioned), don't bump again
