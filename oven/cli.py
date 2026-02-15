import sys
import shlex
from typing import Optional, Tuple


def _extract_backend_arg(args, args_offset: int) -> Tuple[Optional[str], int]:
    """Detect --ogroup/-g <name> in args and return (group_name, new_offset).

    Returns (None, args_offset) if --ogroup/-g is not present.
    """
    if (
        args_offset < len(args)
        and args[args_offset] in ('--ogroup', '-g')
        and args_offset + 1 < len(args)
    ):
        return args[args_offset + 1], args_offset + 2
    return None, args_offset


def _get_baking_cmd(args_offset) -> str:
    """Get the tail of the command line arguments."""
    cmd = shlex.join(sys.argv[args_offset:])
    return cmd.strip()


def ding(args_offset: int = 1) -> None:
    """CLI command `ding`."""
    import oven

    group_name, args_offset = _extract_backend_arg(sys.argv, args_offset)
    if group_name is not None:
        oven.toggle_ogroup(group_name)
    log = ' '.join(sys.argv[args_offset:])
    return oven.get_lazy_oven().ding_log(log)


def bake(args_offset: int = 1) -> None:
    """CLI command `bake`."""
    import oven

    group_name, args_offset = _extract_backend_arg(sys.argv, args_offset)
    if group_name is not None:
        oven.toggle_ogroup(group_name)
    cmd = _get_baking_cmd(args_offset)
    print(f'🍞 Baking: {cmd}')
    return oven.get_lazy_oven().ding_cmd(cmd)


def oven() -> None:
    """CLI command `oven`."""
    if len(sys.argv) < 2:
        from oven.utils import print_manual

        print_manual()
        return

    action = sys.argv[1]
    args = sys.argv[2:]

    if action == 'version':
        from oven.utils import check_version

        check_version()
    elif action == 'help':
        from oven.utils import print_manual

        print_manual()
    elif action == 'ding':
        ding(args_offset=2)
    elif action == 'bake':
        bake(args_offset=2)
    elif action == 'init-cfg':
        from oven.utils import dump_cfg_temp

        dump_cfg_temp(overwrite=False)
    elif action == 'reset-cfg':
        from oven.utils import dump_cfg_temp

        dump_cfg_temp(overwrite=True)
    elif action == 'set-default':
        from oven.utils import set_default

        if len(args) == 0:
            print('Please specify a group name: oven set-default <group>')
        elif len(args) > 1:
            print(f'Unexpected argument {args[1:]}!')
        else:
            set_default(args[0])
    elif action == 'list-ogroups':
        from oven.utils import list_backends

        list_backends()
    elif action == 'home':
        from oven.utils import get_home_path

        print(get_home_path())
    else:
        from oven.utils import error_redirect_to_manual

        error_redirect_to_manual(action)
