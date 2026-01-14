from typing import Dict

from oven.backends.api import Signal, ExpInfoBase, LogInfoBase
from oven.utils.time import (
    timestamp_to_readable,
    seconds_to_adaptive_time_cost,
)


def lines2reply(lines):
    """It changes lines to string block and add quotation mark at the beginning of each line."""
    return '> ' + '\n>\n> '.join(lines).strip()


def plain2md(text):
    text = text.strip().replace('\n', '\n\n')
    return text


LINE_SPLIT = '\n\n'


class DingTalkExpInfo(ExpInfoBase):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> str:
        # 1. Format meta information and time.
        prefix = f'###### [ {self.task_icon} ] {self.readable_time} @ {self.host}'
        # 2. Format current description information.
        msg = self.current_description
        # 3. Concatenate the above two information and return.
        information = (
            prefix
            + LINE_SPLIT
            + self.exp_info
            + LINE_SPLIT
            + self.aux_info
            + LINE_SPLIT
            + msg
        )
        return information

    def custom_signal_handler(self) -> None:
        # Initialization.
        if self.current_signal == Signal.I:
            self.exp_meta_info = self._init_meta()
            # Update the meta information to member variables.
            self.host = self.exp_meta_info['host']
            self.cmd = self.exp_meta_info['cmd']
            self.sec_key = self.exp_meta_info['sec_key']
            return

        # Format the time anyway.
        self.readable_time = timestamp_to_readable(self.current_timestamp)

        # Format the information for later use.
        self.current_description = plain2md(self.current_description)
        if self.current_signal == Signal.S:
            self.exp_info = f'🔥 `{self.cmd}`\n\n' + lines2reply(
                self.current_description.split('\n')
            )
            self.exp_info_backup = self.exp_info
            self.aux_info = ''
        else:
            self.exp_info = lines2reply(self.exp_info_backup.split('\n'))

            cost_info = f'⏱️ **Time Cost**: {seconds_to_adaptive_time_cost(self.current_timestamp - self.start_timestamp)}.'
            if self.current_signal == Signal.P:
                status_info = '🏃 **Running!**'
            elif self.current_signal == Signal.E:
                status_info = '❌ **Error!**'
            elif self.current_signal == Signal.T:
                status_info = '🔔 Done!'
            else:
                assert False, f'Unknown signal: {self.current_signal}'

            self.aux_info = cost_info + LINE_SPLIT + status_info

    # =================== #
    # Customized methods. #
    # =================== #

    def get_title(self) -> str:
        """The title is necessary for DingTalk markdown message."""
        return f'[{self.sec_key}] {self.readable_time} @ {self.host}'

    # ================ #
    # Utils functions. #
    # ================ #

    def _init_meta(self) -> Dict:
        # The host name of the machine where the experiment is running.
        default_host = self.exp_meta_info['default_host']
        custom_host = self.exp_meta_info.get('host', None)
        if custom_host is None:
            host = default_host
        else:
            host = f'{custom_host}({default_host})'
        host = host.strip()

        # Return the validated meta information.
        validated_meta = {
            'host': host,
            'cmd': self.exp_meta_info['cmd'],
            'sec_key': self.exp_meta_info['sec_key'],
        }
        return validated_meta


class DingTalkLogInfo(LogInfoBase, DingTalkExpInfo):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> str:
        # 1. Format meta information and time.
        prefix = f'###### [ {self.task_icon} ] {self.readable_time} @ {self.host}'
        # 2. Format current description information.
        msg = self.current_description
        # 3. Concatenate the above two information and return.
        information = prefix + LINE_SPLIT + msg
        return information

    def custom_signal_handler(self) -> None:
        # Initialization.
        if self.current_signal == Signal.I:
            self.exp_meta_info = self._init_meta()
            # Update the meta information to member variables.
            self.host = self.exp_meta_info['host']
            self.sec_key = self.exp_meta_info['sec_key']
            return

        # Format the time anyway.
        self.readable_time = timestamp_to_readable(self.current_timestamp)
