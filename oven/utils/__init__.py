import os
from typing import Union
from pathlib import Path
from omegaconf import OmegaConf

from .cfg import (
    get_cfg_temp,
    modify_cfg_with_new_backend,
    get_latest_cfg_version,
)
from .version import get_latest_oven_version


def get_home_path() -> Path:
    home_path = None
    if 'OVEN_HOME' in os.environ:
        home_path = Path(os.environ['OVEN_HOME'])
    else:
        from oven.consts import DEFAULT_CFG_HOME

        home_path = Path(DEFAULT_CFG_HOME)
    return home_path


def get_cfg_path() -> Path:
    return get_home_path() / 'cfg.yaml'


def dump_cfg_temp(overwrite: bool = False) -> Union[str, Path]:
    """Download the config template according to latest configuration schema."""
    path = get_cfg_path()

    if not overwrite and Path(path).exists():
        print(f'File already exists: {path}')
    else:
        print(f'Dumping config template to: {path}')
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(get_cfg_temp())
    return path


def toggle_backend(backend: str) -> None:
    cfg_fn = get_cfg_path()
    modify_cfg_with_new_backend(cfg_fn, backend)


def check_version() -> None:
    print('🚧 Experimental function!')
    from oven import __version__

    # Oven version.
    oven_version = __version__.strip()
    try:
        latest_oven_version = get_latest_oven_version().strip()
    except Exception as e:
        print('🥲 Fail to fetch latest oven version.')
        raise e
    if oven_version != latest_oven_version:
        print(
            f'🤔 Local oven version {oven_version} is not up-to-date ({latest_oven_version}), please update.'
        )
    else:
        print(f'🎉 Local oven version ({oven_version}) is up-to-date!')

    # Configuration template version.
    cfg_version = (
        OmegaConf.load(get_cfg_path()).get('version', 'Missing!').strip()
    )
    try:
        latest_cfg_version = get_latest_cfg_version().strip()
    except Exception as e:
        print('🥲 Fail to fetch latest cfg version.')
        raise e
    if cfg_version != latest_cfg_version:
        print(
            f'🤔 Local oven version {cfg_version} is not up-to-date ({latest_cfg_version}), please update.'
        )
    else:
        print(f'🎉 Local config version ({cfg_version}) is up-to-date!')


def print_manual() -> None:
    manual_path = __file__.replace('__init__.py', 'manual.txt')
    with open(manual_path, 'r') as f:
        manual = f.read()
    return print(manual)


def error_redirect_to_manual(action) -> None:
    print(f'😢 Action `{action}` is invalid!')
    return print_manual()
