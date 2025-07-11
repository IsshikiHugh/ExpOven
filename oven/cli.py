import sys


def _get_baking_cmd(args_offset) -> str:
    """Get the tail of the command line arguments."""
    # 1. Get the clean command.
    cmd = ' '.join(sys.argv[args_offset:]).strip()

    # 2. Parse the env variables and manually fix the priority.
    env_vars = []
    cmd_terms = cmd.split(' ')
    for term in cmd.split(' '):
        if '=' in term:
            env_vars.append(term)
            cmd_terms.pop(0)
        else:
            break

    cmd = ''
    if len(env_vars) > 0:
        cmd += ' '.join(env_vars) + ' ; '

    if len(cmd_terms) == 1 and cmd_terms[0] == '':
        print('😵‍💫 No command to bake!')
        exit(1)
    cmd += ' '.join(cmd_terms)

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
    print(f'🍞 Baking: {cmd}')
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
