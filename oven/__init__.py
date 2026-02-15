from typing import Callable, Optional, Dict

from oven.oven import Oven, build_oven
from oven.version import __version__
from oven.progress import progress, progress_range, ProgressBar

# Session-level group name (None = use config.yaml default).
_session_group: Optional[str] = None
_session_group_locked: bool = False
_lazy_oven_obj: Optional[Oven] = None


def toggle_ogroup(group_name: str, force: bool = False) -> None:
    """Switch the notification group for the current session.

    For safety, only the first call takes effect unless ``force=True``.
    Subsequent calls without ``force`` print a warning and are ignored.

    Usage:
    ```
    import oven
    oven.toggle_ogroup('work')
    oven.toggle_ogroup('other')        # ignored, prints warning
    oven.toggle_ogroup('other', force=True)  # takes effect
    ```
    """
    global _session_group, _session_group_locked, _lazy_oven_obj
    if _session_group_locked and not force:
        print(
            f'⚠️ Warning: ogroup already set to "{_session_group}" '
            f'for this session. Use toggle_ogroup("{group_name}", '
            f'force=True) to override.'
        )
        return
    _session_group = group_name
    _session_group_locked = True
    _lazy_oven_obj = None  # Force rebuild on next use.


def get_lazy_oven() -> Optional[Oven]:
    global _lazy_oven_obj
    if _lazy_oven_obj is None:
        _lazy_oven_obj = build_oven(group_name=_session_group)
    return _lazy_oven_obj


# =================================== #
# Utils functions for in-package use. #
# =================================== #


def monitor(func) -> Callable:
    """
    Notifier decorator for a function.

    Usage:
    ```
    @oven.monitor
    def foo() -> None:
        ...
    ```
    It's equivalent to:
    ```
    @oven.bake
    def foo() -> None:
        ...
    ```
    """
    return get_lazy_oven().ding_func(func)


def notify(msg: str) -> None:
    """
    Notify a single message logging.

    Usage:
    ```
    oven.notify('Hello World!')
    ```
    It's equivalent to:
    ```
    oven.ding('Hello World!')
    ```
    """
    return get_lazy_oven().ding_log(msg)


# Interesting alias just for fun, these alias are aligned with CLI.
bake = monitor  # @oven.bake = @oven.monitor
ding = notify  # oven.ding(...) = oven.notify(...)

# Progress tracking functions
# These provide tqdm-like functionality with ExpOven notification support
__all__ = [
    'monitor',
    'notify',
    'bake',
    'ding',
    'toggle_ogroup',
    'progress',
    'progress_range',
    'ProgressBar',
    'get_lazy_oven',
    'Oven',
    'build_oven',
]
