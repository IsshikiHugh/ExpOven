import time
from typing import Union, Dict

from oven.backends.api import Signal, ExpInfoBase, LogInfoBase


def lines2reply(lines):
    """It changes lines to string block and add quotation mark at the beginning of each line."""
    if lines == ['']:
        return ''
    return '> ' + '\n>\n> '.join(lines).strip()


class BarkExpInfo(ExpInfoBase):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> dict:
        # Never send empty paragraph, it would be ugly.

        # Notification level.
        if self.current_signal == Signal.T:
            noti_level = 'active'
        elif self.current_signal == Signal.E:
            noti_level = 'timeSensitive'   # or "critical" if timeSensitive is not working.
        else:
            noti_level = 'passive'

        information = {
            'title': self.exp_info,
            'content': self.aux_info + self.current_description,
            'level': noti_level,
        }
        return information

    def custom_signal_handler(self) -> None:
        # Initialization.
        if self.current_signal == Signal.I:
            self.exp_meta_info = self._init_meta()
            # Update the meta information to member variables.
            self.host = self.exp_meta_info['host']
            self.cmd = self.exp_meta_info['cmd']
            self.device_token = self.exp_meta_info['device_token']
            return

        # Format the time anyway.
        self.readable_time = time.strftime(
            '%a %d %b %Y %I:%M:%S %p %Z',
            time.localtime(self.current_timestamp),
        )

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

            cost_info = f'⏱️ **Time Cost**: {str(self.current_timestamp - self.start_timestamp)}s.'
            if self.current_signal == Signal.P:
                status_info = f'🏃 **Running!**'
            elif self.current_signal == Signal.E:
                status_info = f'❌ **Error!**'
                self.current_description = '\n' + self.current_description
            elif self.current_signal == Signal.T:
                status_info = f'🔔 Done!'
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
            'device_token': self.exp_meta_info['device_token'],
        }
        return validated_meta


class BarkLogInfo(LogInfoBase, BarkExpInfo):

    # ================ #
    # Pre-defined API. #
    # ================ #

    def format_information(self) -> dict:
        information = {
            'title': f'ExpOven Notification',
            'content': self.current_description,
            'level': 'passive',
        }
        return information

    def custom_signal_handler(self) -> None:
        # Initialization.
        if self.current_signal == Signal.I:
            self.exp_meta_info = self._init_meta()
            # Update the meta information to member variables.
            self.host = self.exp_meta_info['host']
            self.device_token = self.exp_meta_info['device_token']
            return

        # Format the time anyway.
        self.readable_time = time.strftime(
            '%a %d %b %Y %I:%M:%S %p %Z',
            time.localtime(self.current_timestamp),
        )
