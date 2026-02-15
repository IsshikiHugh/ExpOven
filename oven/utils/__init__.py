import os
from pathlib import Path

from .version import get_latest_oven_version


_TEMPLATES_DIR = Path(__file__).parent.parent / 'templates'


def _read_bundled_template(filename: str) -> str:
    """Read a bundled template file from oven/templates/."""
    return (_TEMPLATES_DIR / filename).read_text()


def get_home_path() -> Path:
    home_path = None
    if 'OVEN_HOME' in os.environ:
        home_path = Path(os.environ['OVEN_HOME'])
    else:
        from oven.consts import DEFAULT_CFG_HOME

        home_path = Path(DEFAULT_CFG_HOME)
    return home_path


def get_meta_cfg_path() -> Path:
    return get_home_path() / 'config.yaml'


def get_groups_dir() -> Path:
    return get_home_path() / 'ogroups'


def dump_cfg_temp(overwrite: bool = False) -> None:
    """Create config.yaml + ogroups/default.yaml from bundled templates."""
    home = get_home_path()
    meta_path = home / 'config.yaml'
    groups_dir = home / 'ogroups'
    default_group_path = groups_dir / 'default.yaml'

    if not overwrite and meta_path.exists() and default_group_path.exists():
        print(f'Config already exists at: {home}')
        return

    print(f'Dumping config to: {home}')
    groups_dir.mkdir(parents=True, exist_ok=True)

    meta_path.write_text(_read_bundled_template('config.yaml.temp'))
    default_group_path.write_text(_read_bundled_template('group.yaml.temp'))

    print(f'  Created: {meta_path}')
    print(f'  Created: {default_group_path}')


def set_default(group_name: str) -> None:
    """Set the default notification group."""
    groups_dir = get_groups_dir()
    group_path = groups_dir / f'{group_name}.yaml'
    if not group_path.exists():
        print(
            f'Group "{group_name}" not found. ' f'Expected file: {group_path}'
        )
        return

    meta_path = get_meta_cfg_path()
    meta_path.write_text(f'default: {group_name}\n')
    print(f'Default group set to "{group_name}".')


def list_backends() -> None:
    """List all notification groups under ogroups/."""
    groups_dir = get_groups_dir()
    if not groups_dir.exists():
        print('No groups directory found. Run `oven init-cfg` first.')
        return

    from omegaconf import OmegaConf

    # Load default group name
    meta_path = get_meta_cfg_path()
    default_name = None
    if meta_path.exists():
        meta = OmegaConf.load(meta_path)
        default_name = meta.get('default', None)

    group_files = sorted(groups_dir.glob('*.yaml'))
    if not group_files:
        print('No groups found in ogroups/.')
        return

    for gf in group_files:
        name = gf.stem
        marker = ' (default)' if name == default_name else ''
        try:
            cfg = OmegaConf.load(gf)
            backends_list = OmegaConf.to_container(
                cfg.get('backends', []), resolve=True
            )
            if backends_list:
                types = [b.get('type', '?') for b in backends_list if b]
                types_str = ', '.join(types)
            else:
                types_str = '(empty)'
        except Exception:
            types_str = '(invalid)'
        print(f'  {name}{marker}: {types_str}')


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


def print_manual() -> None:
    manual_path = __file__.replace('__init__.py', 'manual.txt')
    with open(manual_path, 'r') as f:
        manual = f.read()
    return print(manual)


def error_redirect_to_manual(action) -> None:
    print(f'😢 Action `{action}` is invalid!')
    return print_manual()
