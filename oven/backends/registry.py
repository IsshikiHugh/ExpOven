"""Backend registry: maps type string → (BackendClass, ExpInfoClass, LogInfoClass)."""

import importlib
from typing import Dict, Tuple, Type

from oven.backends.api import NotifierBackendBase
from oven.backends.api.info import ExpInfoBase, LogInfoBase


# Maps backend type name to (module_path, BackendClass, ExpInfoClass, LogInfoClass)
_REGISTRY: Dict[str, Tuple[str, str, str, str]] = {
    'dingtalk': (
        'oven.backends.dingtalk',
        'DingTalkBackend',
        'DingTalkExpInfo',
        'DingTalkLogInfo',
    ),
    'feishu': (
        'oven.backends.feishu',
        'FeishuBackend',
        'FeishuExpInfo',
        'FeishuLogInfo',
    ),
    'slack': (
        'oven.backends.slack',
        'SlackBackend',
        'SlackExpInfo',
        'SlackLogInfo',
    ),
    'email': (
        'oven.backends.email',
        'EmailBackend',
        'EmailExpInfo',
        'EmailLogInfo',
    ),
}


def get_backend_classes(
    backend_type: str,
) -> Tuple[
    Type[NotifierBackendBase], Type[ExpInfoBase], Type[LogInfoBase]
]:
    """Return (BackendClass, ExpInfoClass, LogInfoClass) for the given type.

    Raises ValueError if the backend type is unknown.
    """
    if backend_type not in _REGISTRY:
        supported = ', '.join(sorted(_REGISTRY))
        raise ValueError(
            f'Unknown backend type "{backend_type}". '
            f'Supported types: {supported}'
        )

    module_path, backend_cls, exp_cls, log_cls = _REGISTRY[backend_type]

    # Lazy import: the backend module + its info module
    pkg = importlib.import_module(module_path)
    info_mod = importlib.import_module(f'{module_path}.info')

    return (
        getattr(pkg, backend_cls),
        getattr(info_mod, exp_cls),
        getattr(info_mod, log_cls),
    )


def supported_types():
    """Return a sorted list of supported backend type strings."""
    return sorted(_REGISTRY)
