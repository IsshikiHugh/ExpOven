from typing import Dict

from oven.backends.api import Signal, ExpInfoBase, LogInfoBase
from oven.backends.api.info import lines2reply
from oven.utils.time import (
    timestamp_to_readable,
    seconds_to_adaptive_time_cost,
)


class FeishuExpInfo(ExpInfoBase):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> dict:
        # Never send empty paragraph, it would be ugly.
        element = []
        parts = [self.exp_info, self.aux_info, self.current_description]
        for part in parts:
            if len(part) > 0:
                element.append(
                    {
                        'tag': 'markdown',
                        'content': part,
                    }
                )

        information = {
            'schema': '2.0',
            'header': {
                'title': {
                    'content': f'{self.readable_time} @ {self.host}',
                    'tag': 'plain_text',
                }
            },
            'body': {
                'elements': element,
            },
        }
        return information

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

    # =================== #
    # Customized methods. #
    # =================== #

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
            'signature': self.exp_meta_info['signature'],
        }
        return validated_meta


class FeishuLogInfo(LogInfoBase, FeishuExpInfo):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> dict:
        information = {
            'schema': '2.0',
            'header': {
                'title': {
                    'content': f'{self.readable_time} @ {self.host}',
                    'tag': 'plain_text',
                },
            },
            'body': {
                'elements': [
                    {
                        'tag': 'markdown',
                        'content': self.current_description,
                    }
                ]
            },
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
