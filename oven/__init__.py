from typing import Callable, Optional

from oven.oven import Oven, build_oven
from oven.version import __version__
from oven.progress import progress, progress_range, ProgressBar

# Global oven.
_lazy_oven_obj: Optional[Oven] = None


def get_lazy_oven() -> Optional[Oven]:
    global _lazy_oven_obj
    if _lazy_oven_obj is None:
        _lazy_oven_obj = build_oven()
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


# 🍟 Interesting alias just for fun, these alias are aligned with CLI.
bake = monitor  # @oven.bake = @oven.monitor
ding = notify  # oven.ding(...) = oven.notify(...)

# Progress tracking functions
# These provide tqdm-like functionality with ExpOven notification support
__all__ = [
    'monitor',
    'notify',
    'bake',
    'ding',
    'progress',
    'progress_range',
    'ProgressBar',
    'get_lazy_oven',
    'Oven',
    'build_oven',
]
