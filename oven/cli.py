import sys


def _get_baking_cmd(args_offset) -> str:
    """Get the tail of the command line arguments."""
    cmd = ''
    is_leading_env = True
    for arg in sys.argv[args_offset:]:
        if '=' in arg and is_leading_env:
            cmd = f'{cmd} {arg}'
        else:
            is_leading_env = False
            cmd = f'{cmd} "{arg}"'  # the double quotes are necessary

    return cmd.strip()


def ding(args_offset: int = 1) -> None:
    """CLI command `ding`."""
    import oven

    log = ' '.join(sys.argv[args_offset:])
    return oven.get_lazy_oven().ding_log(log)


def bake(args_offset: int = 1) -> None:
    """CLI command `bake`."""
    import oven

    cmd = _get_baking_cmd(args_offset)
    print(cmd)
    return oven.get_lazy_oven().ding_cmd(cmd)


def oven() -> None:
    """CLI command `oven`."""
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
    elif action == 'toggle-backend':
        from oven.utils import toggle_backend

        if len(args) == 0:
            print('😵‍💫 Please enter the backend you want to switch to!')
            None
        elif len(args) > 1:
            print(f'😵‍💫 Unexpected argument {args[1:]}!')
        else:
            toggle_backend(args[0])
    elif action == 'home':
        from oven.utils import get_home_path

        print(get_home_path())
    else:
        from oven.utils import error_redirect_to_manual

        error_redirect_to_manual(action)
