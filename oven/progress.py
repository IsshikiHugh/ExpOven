import time
import threading
from typing import Optional, Iterable, Dict

from oven.utils.time import milliseconds_to_adaptive_time_cost
from oven.backends.api import Signal


class ProgressBar:
    """
    A tqdm-like progress bar that also sends notifications to messaging apps.

    This class provides a progress interface similar to tqdm but extends functionality
    to send progress updates to configured messaging backends (DingTalk, Feishu, etc.).

    Supports two modes:
    - HTTP-based (polling-like): Updates sent at regular intervals
    - Socket-based (trigger-like): Updates sent on manual triggers
    """

    def __init__(
        self,
        iterable: Optional[Iterable] = None,
        total: Optional[int] = None,
        desc: str = '',
        unit: str = 'it',
        unit_scale: bool = False,
        disable: bool = False,
        leave: bool = True,
        file=None,
        ncols: Optional[int] = None,
        mininterval: float = 0.1,
        maxinterval: float = 10.0,
        miniters: Optional[int] = None,
        ascii: Optional[bool] = None,
        dynamic_ncols: bool = False,
        smoothing: float = 0.3,
        bar_format: Optional[str] = None,
        initial: int = 0,
        position: Optional[int] = None,
        postfix: Optional[Dict] = None,
        unit_divisor: int = 1000,
        write_bytes: Optional[bool] = None,
        lock_args: Optional[tuple] = None,
        nrows: Optional[int] = None,
        colour: Optional[str] = None,
        delay: float = 0,
        gui: bool = False,
        # ExpOven specific parameters
        notify_interval: float = 30.0,  # Send notification every 30 seconds
        notify_mode: str = 'http',  # "http" or "socket"
        notify_threshold: float = 0.05,  # Notify on 5% progress changes
        enable_notifications: bool = True,
        **kwargs,
    ):
        """
        Initialize the progress bar.

        Args:
            iterable: Iterable to wrap
            total: Total number of iterations
            desc: Description prefix
            notify_interval: Seconds between notifications (HTTP mode)
            notify_mode: "http" (time-based) or "socket" (trigger-based)
            notify_threshold: Minimum progress change to trigger notification
            enable_notifications: Whether to send notifications to messaging apps
            **kwargs: Additional tqdm-compatible parameters
        """
        self.iterable = iterable
        self.total = total or (
            len(iterable) if hasattr(iterable, '__len__') else None
        )
        self.desc = desc
        self.unit = unit
        self.disable = disable
        self.leave = leave
        self.mininterval = mininterval
        self.maxinterval = maxinterval
        self.initial = initial
        self.postfix = postfix or {}

        # ExpOven specific attributes
        self.notify_interval = notify_interval
        self.notify_mode = notify_mode
        self.notify_threshold = notify_threshold
        self.enable_notifications = enable_notifications

        # Progress tracking
        self.n = initial
        self.last_print_n = initial
        self.last_print_time = time.time()
        self.start_time = time.time()
        self.last_notify_time = time.time()
        self.last_notify_progress = 0.0

        # ExpOven integration
        self.exp_info = None
        self._setup_oven_integration()

        # Threading for HTTP mode
        self._stop_thread = False
        self._notify_thread = None
        if self.notify_mode == 'http' and self.enable_notifications:
            self._start_notify_thread()

    def _setup_oven_integration(self):
        """Setup integration with ExpOven notification system."""
        if not self.enable_notifications:
            return

        try:
            # Import here to avoid circular imports
            from oven import get_lazy_oven

            oven = get_lazy_oven()
            if oven:
                meta = oven.backend.get_meta()
                meta['cmd'] = (
                    f'Progress: {self.desc}' if self.desc else 'Progress'
                )
                self.exp_info = oven.ExpInfoClass(
                    backend=oven.backend,
                    exp_meta_info=meta,
                    description=self._format_progress_description(),
                )
        except Exception as e:
            # If oven setup fails, continue without notifications
            self.enable_notifications = False
            print(f'Warning: Could not setup ExpOven notifications: {e}')

    def _format_progress_description(self) -> str:
        """Format the current progress for notifications."""
        if not self.total:
            return f'{self.desc}: {self.n} {self.unit} processed'

        percentage = (self.n / self.total) * 100
        elapsed = time.time() - self.start_time

        if self.n > 0:
            rate = self.n / elapsed
            eta = (self.total - self.n) / rate if rate > 0 else 0
            eta_str = f', ETA: {self._format_time(eta)}'
        else:
            rate = 0
            eta_str = ''

        return (
            f'{self.desc}: {percentage:.1f}% ({self.n}/{self.total}) '
            f'[{self._format_time(elapsed)}<{eta_str}, {rate:.2f}{self.unit}/s]'
        )

    def _format_time(self, seconds: float) -> str:
        """Format time duration in human readable format."""
        formated_time = milliseconds_to_adaptive_time_cost(int(seconds * 1000))
        return formated_time

    def _start_notify_thread(self):
        """Start background thread for HTTP-based notifications."""

        def notify_worker():
            while not self._stop_thread:
                time.sleep(self.notify_interval)
                if not self._stop_thread:
                    self._send_progress_notification()

        self._notify_thread = threading.Thread(
            target=notify_worker, daemon=True
        )
        self._notify_thread.start()

    def _send_progress_notification(self):
        """Send progress notification to messaging apps."""
        if not self.enable_notifications or not self.exp_info:
            return

        current_time = time.time()
        current_progress = (self.n / self.total) if self.total else 0

        # Check if we should send notification based on time and progress thresholds
        time_threshold_met = (
            current_time - self.last_notify_time
        ) >= self.notify_interval
        progress_threshold_met = (
            abs(current_progress - self.last_notify_progress)
            >= self.notify_threshold
        )

        if time_threshold_met or progress_threshold_met:
            try:
                self.exp_info.update_signal(
                    signal=Signal.P,
                    description=self._format_progress_description(),
                )
                self.last_notify_time = current_time
                self.last_notify_progress = current_progress
            except Exception as e:
                print(f'Warning: Failed to send progress notification: {e}')

    def update(self, n: int = 1):
        """Update progress by n steps."""
        self.n += n
        self._refresh()

        # For socket mode, send notification on manual updates
        if self.notify_mode == 'socket':
            self._send_progress_notification()

    def _refresh(self):
        """Refresh the terminal display."""
        if self.disable:
            return

        current_time = time.time()
        if (current_time - self.last_print_time) >= self.mininterval:
            self._display_progress()
            self.last_print_time = current_time
            self.last_print_n = self.n

    def _display_progress(self):
        """Display progress bar in terminal (simplified tqdm-like display)."""
        if self.disable:
            return

        # Simple progress bar display
        if self.total:
            percentage = (self.n / self.total) * 100
            bar_length = 30
            filled_length = int(bar_length * self.n // self.total)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)

            elapsed = time.time() - self.start_time
            rate = self.n / elapsed if elapsed > 0 else 0

            print(
                f'\r{self.desc}: {percentage:6.2f}%|{bar}| {self.n}/{self.total} '
                f'[{self._format_time(elapsed)}, {rate:.2f}{self.unit}/s]',
                end='',
                flush=True,
            )
        else:
            elapsed = time.time() - self.start_time
            rate = self.n / elapsed if elapsed > 0 else 0
            print(
                f'\r{self.desc}: {self.n}{self.unit} '
                f'[{self._format_time(elapsed)}, {rate:.2f}{self.unit}/s]',
                end='',
                flush=True,
            )

    def __iter__(self):
        """Make this object iterable."""
        if self.iterable is None:
            raise TypeError("'ProgressBar' object is not iterable")

        for item in self.iterable:
            yield item
            self.update(1)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the progress bar and clean up."""
        if self._notify_thread:
            self._stop_thread = True
            self._notify_thread.join(timeout=1.0)

        if self.enable_notifications and self.exp_info:
            try:
                # Send final notification
                if self.total and self.n >= self.total:
                    self.exp_info.update_signal(
                        signal=Signal.T, description='Progress completed!'
                    )
                else:
                    self.exp_info.update_signal(
                        signal=Signal.T,
                        description=self._format_progress_description(),
                    )
            except Exception as e:
                print(f'Warning: Failed to send final notification: {e}')

        if not self.disable and self.leave:
            print()  # New line after progress bar

    def set_description(self, desc: str):
        """Set the description prefix."""
        self.desc = desc

    def set_postfix(self, **kwargs):
        """Set postfix values."""
        self.postfix.update(kwargs)


# Convenience functions similar to tqdm
def progress(
    iterable=None,
    desc='',
    total=None,
    leave=True,
    file=None,
    ncols=None,
    mininterval=0.1,
    maxinterval=10.0,
    miniters=None,
    ascii=None,
    disable=False,
    unit='it',
    unit_scale=False,
    dynamic_ncols=False,
    smoothing=0.3,
    bar_format=None,
    initial=0,
    position=None,
    postfix=None,
    unit_divisor=1000,
    write_bytes=None,
    lock_args=None,
    nrows=None,
    colour=None,
    delay=0,
    gui=False,
    # ExpOven specific
    notify_interval=30.0,
    notify_mode='http',
    notify_threshold=0.05,
    enable_notifications=True,
    **kwargs,
):
    """
    A tqdm-like progress bar with ExpOven notification support.

    Args:
        iterable: Iterable to wrap
        desc: Description prefix
        notify_interval: Seconds between notifications (HTTP mode)
        notify_mode: "http" (time-based) or "socket" (trigger-based)
        notify_threshold: Minimum progress change to trigger notification
        enable_notifications: Whether to send notifications to messaging apps
        **kwargs: Additional parameters

    Returns:
        ProgressBar instance
    """
    return ProgressBar(
        iterable=iterable,
        desc=desc,
        total=total,
        leave=leave,
        file=file,
        ncols=ncols,
        mininterval=mininterval,
        maxinterval=maxinterval,
        miniters=miniters,
        ascii=ascii,
        disable=disable,
        unit=unit,
        unit_scale=unit_scale,
        dynamic_ncols=dynamic_ncols,
        smoothing=smoothing,
        bar_format=bar_format,
        initial=initial,
        position=position,
        postfix=postfix,
        unit_divisor=unit_divisor,
        write_bytes=write_bytes,
        lock_args=lock_args,
        nrows=nrows,
        colour=colour,
        delay=delay,
        gui=gui,
        notify_interval=notify_interval,
        notify_mode=notify_mode,
        notify_threshold=notify_threshold,
        enable_notifications=enable_notifications,
        **kwargs,
    )


def progress_range(*args, **kwargs):
    """
    A shortcut for progress(range(*args), **kwargs).
    """
    return progress(range(*args), **kwargs)
