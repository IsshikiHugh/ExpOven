# Progress Notification Interface

ExpOven now includes a **tqdm-like progress interface** that not only displays progress bars in the terminal but also sends progress notifications to your configured messaging apps (DingTalk, Feishu, Email, etc.).

## Overview

The progress interface provides:

- **Terminal progress bars** similar to tqdm
- **Real-time notifications** to messaging apps
- **Two notification modes**: HTTP-based (time intervals) and Socket-based (trigger-based)
- **Flexible configuration** for notification frequency and thresholds

## Quick Start

### Basic Usage

```python
import oven
import time

# Simple progress bar for a range
for i in oven.progress_range(100, desc="Processing"):
    time.sleep(0.1)  # Your work here

# Progress bar wrapping an iterable
data = [f"item_{i}" for i in range(50)]
for item in oven.progress(data, desc="Processing items"):
    # Process each item
    time.sleep(0.1)

# Manual progress updates
with oven.ProgressBar(total=200, desc="Manual updates") as pbar:
    for batch in range(10):
        # Process batch
        time.sleep(0.5)
        pbar.update(20)  # Update by 20 items
```

### With Notifications

```python
# HTTP mode: sends notifications at regular time intervals
for i in oven.progress_range(
    100,
    desc="Long running task",
    notify_mode="http",
    notify_interval=30.0,  # Notify every 30 seconds
    notify_threshold=0.1   # Or when 10% progress is made
):
    time.sleep(0.5)

# Socket mode: sends notifications on manual triggers
with oven.ProgressBar(
    total=100,
    desc="Batch processing",
    notify_mode="socket",
    notify_threshold=0.05  # Notify on 5% progress changes
) as pbar:
    for batch in range(10):
        # Process batch
        process_batch()
        pbar.update(10)  # Notification sent automatically
```

## API Reference

### `oven.progress(iterable, **kwargs)`

Wrap an iterable with a progress bar.

**Parameters:**

- `iterable`: The iterable to wrap
- `desc`: Description prefix for the progress bar
- `total`: Total number of iterations (auto-detected for most iterables)
- `notify_mode`: `"http"` (time-based) or `"socket"` (trigger-based)
- `notify_interval`: Seconds between notifications (HTTP mode)
- `notify_threshold`: Minimum progress change to trigger notification
- `enable_notifications`: Whether to send notifications to messaging apps
- All other tqdm-compatible parameters

### `oven.progress_range(*args, **kwargs)`

Shortcut for `oven.progress(range(*args), **kwargs)`.

### `oven.ProgressBar(total, **kwargs)`

Manual progress bar for custom update patterns.

**Methods:**

- `update(n)`: Update progress by n steps
- `set_description(desc)`: Change the description
- `set_postfix(**kwargs)`: Set postfix values
- `close()`: Close and send final notification

## Notification Modes

### HTTP Mode (Polling-like)

```python
# Sends notifications at regular time intervals
for i in oven.progress_range(
    1000,
    notify_mode="http",
    notify_interval=60.0,  # Every 60 seconds
    notify_threshold=0.1   # Or every 10% progress
):
    # Your work here
    pass
```

**Characteristics:**

- Notifications sent on time intervals
- Background thread handles notifications
- Good for long-running tasks
- Reduces notification spam

### Socket Mode (Trigger-like)

```python
# Sends notifications on progress updates
with oven.ProgressBar(
    total=100,
    notify_mode="socket",
    notify_threshold=0.05  # Every 5% progress
) as pbar:
    for i in range(100):
        # Your work here
        pbar.update(1)  # Notification sent if threshold met
```

**Characteristics:**

- Notifications sent on manual updates
- Immediate feedback on progress changes
- Good for interactive tasks
- More responsive but potentially more notifications

## Configuration

### Notification Settings

```python
# Customize notification behavior
progress_bar = oven.ProgressBar(
    total=1000,
    desc="Custom task",

    # Notification settings
    notify_mode="http",           # or "socket"
    notify_interval=30.0,         # seconds (HTTP mode)
    notify_threshold=0.05,        # 5% progress change
    enable_notifications=True,    # enable/disable notifications

    # Standard tqdm settings
    unit="items",
    unit_scale=True,
    leave=True
)
```

### Backend Configuration

Make sure ExpOven is configured with your preferred messaging backend:

```bash
# Initialize configuration
oven init-cfg

# Edit ~/.config/oven/cfg.yaml to configure your backend
# (DingTalk, Feishu, Email, etc.)
```

## Examples

### Machine Learning Training

```python
import oven

def train_model(epochs=100):
    for epoch in oven.progress_range(epochs, desc="Training"):
        # Training logic
        train_loss = train_epoch()
        val_loss = validate_epoch()

        # Update progress with metrics
        if hasattr(oven, '_current_progress'):
            oven._current_progress.set_postfix(
                train_loss=f"{train_loss:.4f}",
                val_loss=f"{val_loss:.4f}"
            )
```

### Data Processing Pipeline

```python
import oven

def process_files(file_list):
    # Process files with progress tracking
    for file_path in oven.progress(file_list, desc="Processing files"):
        process_file(file_path)

    # Batch processing with manual updates
    with oven.ProgressBar(total=len(file_list), desc="Post-processing") as pbar:
        for i in range(0, len(file_list), 10):  # Process in batches of 10
            batch = file_list[i:i+10]
            post_process_batch(batch)
            pbar.update(len(batch))
```

### Long-running Experiments

```python
import oven

def run_experiment():
    # Long experiment with periodic notifications
    for trial in oven.progress_range(
        1000,
        desc="Running experiment",
        notify_mode="http",
        notify_interval=300,  # Notify every 5 minutes
        notify_threshold=0.01  # Or every 1% progress
    ):
        result = run_trial(trial)
        if result.is_significant():
            oven.notify(f"Significant result found at trial {trial}")
```

## Best Practices

1. **Choose the right mode**:
   - Use HTTP mode for long-running tasks (>30 minutes)
   - Use socket mode for interactive or shorter tasks

2. **Set appropriate thresholds**:
   - Lower thresholds (1-5%) for important tasks
   - Higher thresholds (10-20%) for routine tasks

3. **Combine with regular notifications**:
   ```python
   for i in oven.progress_range(1000, desc="Processing"):
       result = process_item(i)
       if result.has_error():
           oven.notify(f"Error at item {i}: {result.error}")
   ```

4. **Use descriptive messages**:
   ```python
   pbar = oven.ProgressBar(total=100, desc="Model training - Epoch 1/10")
   pbar.set_postfix(lr=0.001, loss=0.5, acc=0.85)
   ```

## Troubleshooting

### No notifications received
- Check ExpOven configuration: `oven help`
- Verify backend settings in `~/.config/oven/cfg.yaml`
- Test basic notifications: `oven.notify("Test message")`

### Progress bar not displaying
- Check if `disable=True` is set
- Verify terminal supports progress bars
- Try `enable_notifications=False` to isolate issues

### Performance issues
- Increase `notify_interval` for HTTP mode
- Increase `notify_threshold` to reduce notification frequency
- Use `mininterval` to control terminal update frequency

## Migration from tqdm

ExpOven's progress interface is designed to be a drop-in replacement for tqdm:

```python
# Before (tqdm)
from tqdm import tqdm, trange
for i in tqdm(range(100), desc="Processing"):
    pass

# After (ExpOven)
import oven
for i in oven.progress_range(100, desc="Processing"):
    pass
```

Additional ExpOven-specific parameters can be added without breaking existing code.
