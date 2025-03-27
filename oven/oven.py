import sys
import traceback
import subprocess
from typing import Type, Callable, Any, Union
from pathlib import Path
from omegaconf import OmegaConf

from oven.backends.api import (
    NotifierBackendBase,
    ExpInfoBase,
    LogInfoBase,
    Signal,
)
from oven.utils import get_cfg_path


class Oven:
    def __init__(self, cfg) -> None:
        self.cfg = cfg

        # Register some important classes.
        self.ExpInfoClass: Type[ExpInfoBase]
        self.LogInfoClass: Type[LogInfoBase]
        self.backend: NotifierBackendBase
        self._init_notifier()

    def ding_log(self, msg: str) -> None:
        """Notify a single log information."""
        meta = self.backend.get_meta()
        log_info = self.LogInfoClass(
            self.backend, exp_meta_info=meta, description=msg
        )

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

            # Start the experiment.
            meta = self.backend.get_meta()
            meta['cmd'] = f'{func.__name__}({args_info})'
            exp_info = self.ExpInfoClass(
                backend=self.backend, exp_meta_info=meta
            )

            try:
                # Running the experiment.
                resp = func(*args, **kwargs)
            except Exception as e:
                # Finish baking with error.
                exp_info.update_signal(
                    signal=Signal.E,
                    description=f'Function internal exception detected: {e}',
                )
                return None

            # Experiment finished.
            exp_info.update_signal(signal=Signal.T)
            return resp

        return inner

    def ding_cmd(self, cmd: str) -> None:
        """Run a command and notify before & after the command."""
        meta = self.backend.get_meta()
        meta['cmd'] = cmd.strip()
        exp_info = self.ExpInfoClass(backend=self.backend, exp_meta_info=meta)

        try:
            # run command, then capture output and error.
            subprocess.run(cmd, shell=True, check=True, encoding='utf-8')
        except subprocess.CalledProcessError as e:
            # Finish baking with error.
            exp_info.update_signal(
                signal=Signal.E, description=f'Command error detected: {e}'
            )
            return None

        # Experiment finished.
        exp_info.update_signal(signal=Signal.T)

    def _init_notifier(self) -> None:
        """Initialize the notifier."""
        # 1. Through useless things.
        backend = self.cfg.backend
        self.cfg = self.cfg[backend]
        self.cfg['backend'] = backend
        if backend == 'dingtalk':
            from oven.backends.dingtalk import (
                DingTalkBackend,
                DingTalkExpInfo,
                DingTalkLogInfo,
            )

            self.ExpInfoClass = DingTalkExpInfo
            self.LogInfoClass = DingTalkLogInfo
            self.backend = DingTalkBackend(self.cfg)
        elif backend == 'feishu':
            from oven.backends.feishu import (
                FeishuBackend,
                FeishuExpInfo,
                FeishuLogInfo,
            )

            self.ExpInfoClass = FeishuExpInfo
            self.LogInfoClass = FeishuLogInfo
            self.backend = FeishuBackend(self.cfg)
        elif backend == 'email':
            from oven.backends.email import (
                EmailBackend,
                EmailExpInfo,
                EmailLogInfo,
            )

            self.ExpInfoClass = EmailExpInfo
            self.LogInfoClass = EmailLogInfo
            self.backend = EmailBackend(self.cfg)
        else:
            self.ExpInfoClass = ...
            self.LogInfoClass = ...
            self.backend = ...
            raise NotImplementedError(
                f'Notifier backend `{backend}` is not supported yet.'
            )


def build_oven(
    cfg_path: Union[Path, str] = None, raise_err: bool = False
) -> Oven:
    cfg_path = get_cfg_path()
    oven = None

    try:
        if not Path(cfg_path).exists():
            raise FileNotFoundError(
                f'Oven configuration file not found at `{cfg_path}`.'
            )
        cfg = OmegaConf.load(cfg_path)
        oven = Oven(cfg)
    except Exception as e:
        # Generate tips.
        searched_paths = f'\n- {cfg_path}'
        print(
            f'Oven configuration file not found or invalid: {searched_paths}'
        )
        print(
            'You are suggested to set the environment variable `OVEN_HOME` to the directory containing the `cfg.yaml`, or ensure the validity of config files mentioned.'
        )
        print(f'Error: {e}')

        if raise_err:
            traceback.print_exc()
            raise e
        else:
            sys.exit(1)
    return oven
