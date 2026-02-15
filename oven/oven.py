import sys
import traceback
import subprocess
from typing import Type, List, Dict, Callable, Any, Optional
from pathlib import Path
from omegaconf import OmegaConf

from oven.backends.api import (
    NotifierBackendBase,
    ExpInfoBase,
    LogInfoBase,
    Signal,
)
from oven.backends.registry import get_backend_classes


class Oven:
    def __init__(self, group_name: str, group_cfg: List[Dict]) -> None:
        self.group_name = group_name

        # Lists — one entry per backend in the group.
        self.backends: List[NotifierBackendBase] = []
        self.exp_info_classes: List[Type[ExpInfoBase]] = []
        self.log_info_classes: List[Type[LogInfoBase]] = []

        for entry in group_cfg:
            backend_type = entry['type']
            BackendCls, ExpInfoCls, LogInfoCls = get_backend_classes(
                backend_type
            )
            self.backends.append(BackendCls(entry))
            self.exp_info_classes.append(ExpInfoCls)
            self.log_info_classes.append(LogInfoCls)

    def ding_log(self, msg: str) -> None:
        """Notify a single log information to all backends in the group."""
        for backend, LogInfoCls in zip(self.backends, self.log_info_classes):
            meta = backend.get_meta()
            LogInfoCls(backend, exp_meta_info=meta, description=msg)

    def ding_func(self, func: Callable) -> Callable:
        """Function decorator to notify the experiment information."""

        def inner(*args, **kwargs) -> Any:
            # Generate function information.
            n_args = len(args)
            n_kwargs = len(kwargs.keys())
            args_info = ''
            if n_args > 0:
                args_info += f', #args={n_args}'
            if n_kwargs > 0:
                args_info += f', #kwargs={n_kwargs}'
                kwargs_keys = list(kwargs.keys())
                if n_kwargs <= 5:
                    kwargs_keys = ', '.join(kwargs_keys)
                    args_info += f', kwargs={kwargs_keys} )'
                else:
                    kwargs_keys = ', '.join(kwargs_keys[:5])
                    args_info += f', kwargs={kwargs_keys}...'
            if len(args_info) > 2:
                args_info = args_info[2:]

            # Start the experiment on all backends.
            exp_infos = []
            for backend, ExpInfoCls in zip(
                self.backends, self.exp_info_classes
            ):
                meta = backend.get_meta()
                meta['cmd'] = f'{func.__name__}({args_info})'
                exp_infos.append(
                    ExpInfoCls(backend=backend, exp_meta_info=meta)
                )

            try:
                # Running the experiment.
                resp = func(*args, **kwargs)
            except Exception as e:
                # Finish baking with error.
                for exp_info in exp_infos:
                    exp_info.update_signal(
                        signal=Signal.E,
                        description=f'Function internal exception detected: {e}',
                    )
                traceback.print_exc()
                return None

            # Experiment finished.
            for exp_info in exp_infos:
                exp_info.update_signal(signal=Signal.T)
            return resp

        return inner

    def ding_cmd(self, cmd: str) -> None:
        """Run a command and notify before & after the command."""
        exp_infos = []
        for backend, ExpInfoCls in zip(self.backends, self.exp_info_classes):
            meta = backend.get_meta()
            meta['cmd'] = cmd.strip()
            exp_infos.append(ExpInfoCls(backend=backend, exp_meta_info=meta))

        try:
            # run command, then capture output and error.
            subprocess.run(cmd, shell=True, check=True, encoding='utf-8')
        except subprocess.CalledProcessError as e:
            # Finish baking with error.
            for exp_info in exp_infos:
                exp_info.update_signal(
                    signal=Signal.E,
                    description=f'Command error detected: {e}',
                )
            traceback.print_exc()
            return None

        # Experiment finished.
        for exp_info in exp_infos:
            exp_info.update_signal(signal=Signal.T)


def _load_default_group_name() -> str:
    """Load the default group name from config.yaml."""
    from oven.utils import get_meta_cfg_path

    meta_path = get_meta_cfg_path()
    if not meta_path.exists():
        raise FileNotFoundError(
            f'Meta config not found at {meta_path}. '
            'Run `oven init-cfg` to create it.'
        )
    meta = OmegaConf.load(meta_path)
    return meta.get('default', 'default')


def _load_group_config(group_name: str) -> List[Dict]:
    """Load a group config file and return its backends list."""
    from oven.utils import get_groups_dir

    group_path = get_groups_dir() / f'{group_name}.yaml'
    if not group_path.exists():
        raise FileNotFoundError(f'Group config not found at {group_path}.')
    cfg = OmegaConf.load(group_path)
    backends_list = OmegaConf.to_container(
        cfg.get('backends', []), resolve=True
    )
    if not backends_list:
        raise ValueError(
            f'Group "{group_name}" has no backends configured. '
            f'Edit {group_path} to add at least one backend.'
        )
    return backends_list


def build_oven(
    group_name: Optional[str] = None,
    raise_err: bool = False,
) -> Oven:
    oven = None

    try:
        if group_name is None:
            group_name = _load_default_group_name()
        group_cfg = _load_group_config(group_name)
        oven = Oven(group_name, group_cfg)
    except Exception as e:
        from oven.utils import get_home_path

        print(f'Failed to build oven: {e}')
        print(
            f'Config home: {get_home_path()}\n'
            'Run `oven init-cfg` to create the config, then edit '
            'ogroups/default.yaml to configure your backends.'
        )

        if raise_err:
            traceback.print_exc()
            raise e
        else:
            sys.exit(1)
    return oven
