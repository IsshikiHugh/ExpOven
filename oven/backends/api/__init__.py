from abc import ABC, abstractmethod
from typing import Union, Dict

from .info import *


class RespStatus:
    def __init__(self, has_err: bool, err_msg: str = '') -> None:
        self.has_err: bool = has_err
        self.err_msg: str = err_msg


class NotifierBackendBase(ABC):

    # ========================================== #
    # Functions below should/can be overwritten. #
    # ========================================== #

    def __init__(self, cfg: Dict) -> None:
        """Read necessary information from config file. And validate the configuration."""

    @abstractmethod
    def notify(self, info: ExpInfoBase) -> RespStatus:
        ...

    @abstractmethod
    def get_meta(self) -> Dict:
        """Generate meta information for information object."""
        ...
