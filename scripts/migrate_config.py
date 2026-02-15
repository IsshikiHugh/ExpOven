#!/usr/bin/env python
"""Migrate ExpOven config from old single-file format (cfg.yaml) to new group format.

Old layout:
  ~/.config/oven/cfg.yaml        # single file, all backends in one

New layout:
  ~/.config/oven/config.yaml     # meta config (default group)
  ~/.config/oven/ogroups/         # one YAML per backend
    default.yaml                  # the previously active backend
    <type>.yaml                   # each other configured backend

Each backend section in the old config becomes its own group file.
The previously active backend (old ``backend:`` field) is written to
``default.yaml``; every other configured backend gets a file named
after its type (e.g. ``feishu.yaml``).  Backend sections that contain
only placeholders (``<?>``) are skipped.

Usage:
  python scripts/migrate_config.py            # uses default OVEN_HOME
  python scripts/migrate_config.py /path/to   # explicit config directory
"""

import os
import sys
import shutil
from pathlib import Path

# Keys in old cfg.yaml that are metadata, not backend sections.
_META_KEYS = {'backend', 'version'}


def _resolve_home(explicit_path=None):
    if explicit_path:
        return Path(explicit_path)
    if 'OVEN_HOME' in os.environ:
        return Path(os.environ['OVEN_HOME'])
    return Path.home() / '.config' / 'oven'


def _is_placeholder_only(section_dict):
    """Return True if every value is a placeholder or None."""
    for v in section_dict.values():
        if v is not None and '<?>' not in str(v):
            return False
    return True


def _build_group_yaml(backend_type, section_dict):
    """Build a group YAML string for one backend."""
    lines = ['backends:']
    lines.append(f'  - type: {backend_type}')
    for key, value in section_dict.items():
        lines.append(f'    {key}: {value}')
    return '\n'.join(lines) + '\n'


def migrate(home):
    old_cfg_path = home / 'cfg.yaml'

    if not old_cfg_path.exists():
        print(f'No old config found at {old_cfg_path}, nothing to migrate.')
        return False

    # Read old config.
    try:
        from omegaconf import OmegaConf

        old_cfg = OmegaConf.load(old_cfg_path)
        old_dict = OmegaConf.to_container(old_cfg, resolve=True)
    except Exception as e:
        print(f'Failed to load old config: {e}')
        return False

    active_backend = old_dict.get('backend', None)
    if not active_backend:
        print('Old config has no "backend" field, nothing to migrate.')
        return False

    # Collect all backend sections (skip meta keys).
    backend_sections = {}
    for key, value in old_dict.items():
        if key in _META_KEYS:
            continue
        if not isinstance(value, dict):
            continue
        backend_sections[key] = value

    if not backend_sections:
        print('Old config has no backend sections, nothing to migrate.')
        return False

    # Create new structure.
    groups_dir = home / 'ogroups'
    groups_dir.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []

    for backend_type, section in backend_sections.items():
        if _is_placeholder_only(section):
            skipped.append(backend_type)
            continue

        # Active backend → default.yaml, others → <type>.yaml.
        if backend_type == active_backend:
            filename = 'default.yaml'
        else:
            filename = f'{backend_type}.yaml'

        group_path = groups_dir / filename
        group_path.write_text(_build_group_yaml(backend_type, section))
        created.append((backend_type, group_path))

    # Write meta config.
    meta_path = home / 'config.yaml'
    meta_path.write_text('default: default\n')

    # Back up old config.
    backup_path = old_cfg_path.with_suffix('.yaml.bak')
    shutil.copy2(old_cfg_path, backup_path)
    old_cfg_path.unlink()

    # Report.
    print('Migration complete!')
    print(f'  Old config backed up to: {backup_path}')
    print(f'  Created: {meta_path}')
    for backend_type, group_path in created:
        label = ' (default)' if backend_type == active_backend else ''
        print(f'  Created: {group_path}  [{backend_type}{label}]')
    if skipped:
        print(f'  Skipped (placeholder-only): {", ".join(skipped)}')
    return True


def main():
    explicit = sys.argv[1] if len(sys.argv) > 1 else None
    home = _resolve_home(explicit)
    print(f'Config home: {home}')
    migrate(home)


if __name__ == '__main__':
    main()
