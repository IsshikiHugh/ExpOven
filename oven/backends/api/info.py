import random
import socket
from typing import Optional, Dict
from oven.utils.time import get_current_timestamp

# fmt: off
EMOJI_TASK_ICON_POOL = [
    '🍎', '🍊', '🍌', '🍉', '🍇', '🍓', '🍍', '🍒', '🍑', '🍐', '🍋', '🥝', '🥥', '🥭',
    '🥦', '🥕', '🌽', '🍆', '🍅', '🥔', '🍠', '🥬', '🥒', '🍄', '🫑', '🧅', '🧄', "🍄",
    '🌵', '🌲', '🌿', '🍀', '🍁', '🌸', '🌻', '☀️', '🌙', '🌈', '🌊',
    '🔮', '💎', '👻', '👽', '🤖', '🎃', '🐙', '🦋', '🦖', '🦄', '🦜',
]
# fmt: on


class Signal:
    U = -1  # unknown
    I = 0  # initialization
    S = 1  # start
    P = 2  # progress
    T = 3  # terminate
    E = 4  # exception

    @staticmethod
    def is_valid(signal):
        return signal in [
            Signal.U,
            Signal.I,
            Signal.S,
            Signal.P,
            Signal.T,
            Signal.E,
        ]

    @staticmethod
    def is_noisy(signal):
        return signal in [Signal.S, Signal.P, Signal.T, Signal.E]


class ExpInfoBase:
    """
    ExpInfo is used for long running experiments. Unlike normal logging information, the notifier may be
    triggered multiple times during the experiment to inform the user about the current progress.
    Sometimes, it is responsible for reporting the exceptions as well. The working pipeline is shown below:

      ┌─────────┐◄────────┐    ┌─────────┐
      │ ExpOven │◄────┐   │    │ ExpOven │◄────┐
      └─────────┘◄┐   │   │    └─────────┘◄┐   │
      ▲   ▲   ▲   │   │   │    ▲   ▲   ▲   │   │
     S│  P│  P│  P│  P│  E│   S│  P│  P│  P│  !│
      │◄──┴─── Exp ───┴──►│    │◄──┴─── Exp ───⚡

    Signals explanation:
    - S means start point, it's triggered through  `__init__()`
    - P means intermediate progress reporting, it's triggered through `progress_report()`
    - T means the experiment is terminated normally, it's triggered through `terminate_report()`
    - E means the experiment ends with an exception, it's triggered through `exception_report()`

    The `format_information()` should be implemented to format the logging information. The style can be
    closely related to the notifier backend.
    The `custom_signal_handler()` is used to customize signal handling. It will be triggered each time the
    information is updated. It's not necessary to be implemented.
    """

    def __init__(
        self,
        backend,
        exp_meta_info: Dict = {},
        description: Optional[str] = '',
    ) -> None:
        """Initialize the experiment logging information when it starts."""
        self.backend = backend  # store the reference of backend

        # Initialization.
        exp_meta_info['default_host'] = socket.gethostname()
        self.exp_meta_info = exp_meta_info
        self.current_signal = Signal.I
        self._safe_signal_handler()
        self.task_icon = random.choice(EMOJI_TASK_ICON_POOL)

        # Start.
        self.current_signal = Signal.S
        self.current_description = description
        self.current_timestamp = get_current_timestamp()
        self.start_timestamp = self.current_timestamp
        self._safe_signal_handler()

    def _safe_signal_handler(self) -> None:
        try:
            assert Signal.is_valid(self.current_signal), 'Invalid signal.'
            # Get trigger time.
            self.current_timestamp = get_current_timestamp()
        except AssertionError:
            # Detect signal validity.
            self.current_signal = Signal.E
            self.current_description = (
                f'Invalid signal {self.current_signal} detected.'
            )
        except Exception as e:
            # Handle other exceptions.
            self.current_signal = Signal.E
            self.current_description = f'Oven internal exception detected: {e}'
        finally:
            self.custom_signal_handler()

        # Trigger notifier backend.
        if Signal.is_noisy(self.current_signal):
            resp = self.backend.notify(self)
            if resp.has_err:
                raise ConnectionError(
                    f'Notifier backend error detected: {resp.err_msg}'
                )

    def update_signal(
        self, signal: int, description: Optional[str] = ''
    ) -> None:
        """Update the signal and description."""
        self.current_signal = signal
        self.current_description = description

        self._safe_signal_handler()

    # ========================================== #
    # Functions below should/can be overwritten. #
    # ========================================== #

    def format_information(self) -> str:
        """Format the experiment logging information."""
        raise NotImplementedError

        # 1. Format meta information and time.
        # 2. Format current description information.
        # 3. Concatenate the above two information and return.

    def custom_signal_handler(self) -> None:
        """Extra process for different signals. Not necessary to be implemented."""


class LogInfoBase:
    """
    Info is used for single logging message. In order to implement this, you can simply inherit the classes
    like `class MyLogInfo(LogInfoBase, MyExpInfo):`.
    """

    def __init__(
        self,
        backend,
        exp_meta_info: Optional[Dict] = None,
        description: Optional[str] = '',
    ) -> None:
        """Initialize the experiment logging information when it starts."""
        self.backend = backend  # store the reference of backend

        # Initialization.
        exp_meta_info['default_host'] = socket.gethostname()
        exp_meta_info['cmd'] = ''  # hack cmd
        self.exp_meta_info = exp_meta_info
        self.current_signal = Signal.I
        self._safe_signal_handler()
        self.task_icon = '🔈'

        # Terminate early.
        self.current_signal = (
            Signal.T
        )  # single logging is regarded as an experiment terminated directly
        self.current_description = description

        self._safe_signal_handler()
