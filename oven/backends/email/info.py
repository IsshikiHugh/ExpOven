from typing import Dict

from oven.backends.api import Signal, ExpInfoBase, LogInfoBase
from oven.backends.api.info import lines2reply
from oven.utils.time import (
    timestamp_to_readable,
    seconds_to_adaptive_time_cost,
)


class EmailExpInfo(ExpInfoBase):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> dict:
        # Never send empty paragraph, it would be ugly.

        element = self.exp_info
        if len(self.aux_info) > 0:
            element += '\n' + self.aux_info + '\n'
        if len(self.current_description) > 0:
            element += self.current_description
        information = {
            'subject': f'{self.readable_time} @ {self.host}',
            'content': element,
        }
        return information

    # =================== #
    # Customized methods. #
    # =================== #

    def custom_signal_handler(self) -> None:
        # Initialization.
        if self.current_signal == Signal.I:
            self.exp_meta_info = self._init_meta()
            # Update the meta information to member variables.
            self.host = self.exp_meta_info['host']
            self.cmd = self.exp_meta_info['cmd']
            self.signature = self.exp_meta_info['signature']
            return

        # Format the time anyway.
        self.readable_time = timestamp_to_readable(self.current_timestamp)

        # Format the information for later use.
        self.current_description = self.current_description
        if self.current_signal == Signal.S:
            if self.current_description == '':
                self.exp_info = f'🔥 `{self.cmd}`'
            else:
                self.exp_info = f'🔥 `{self.cmd}`\n' + lines2reply(
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

            self.aux_info = '\n'.join([cost_info, status_info])

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
            'signature': None,
        }
        return validated_meta


class EmailLogInfo(LogInfoBase, EmailExpInfo):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> dict:
        information = {
            'subject': f'{self.readable_time} @ {self.host}',
            'content': self.current_description,
        }
        return information

    def custom_signal_handler(self) -> None:
        # Initialization.
        if self.current_signal == Signal.I:
            self.exp_meta_info = self._init_meta()
            # Update the meta information to member variables.
            self.host = self.exp_meta_info['host']
            self.signature = self.exp_meta_info['signature']
            return

        # Format the time anyway.
        self.readable_time = timestamp_to_readable(self.current_timestamp)
