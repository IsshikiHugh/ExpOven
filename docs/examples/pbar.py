"""
Examples demonstrating the new progress notification interface in ExpOven.

This module shows how to use the tqdm-like progress interface that also
sends notifications to messaging apps (DingTalk, Feishu, Email, etc.).
"""

import time
import random
import oven


def example_basic_progress():
    """Basic progress bar example - similar to tqdm."""
    print('=== Basic Progress Bar Example ===')

    # Simple progress bar for a range
    for i in oven.progress_range(100, desc='Processing'):
        time.sleep(0.05)  # Simulate work

    print('Basic progress completed!\n')


def example_iterable_progress():
    """Progress bar wrapping an iterable."""
    print('=== Iterable Progress Example ===')

    data = [f'item_{i}' for i in range(50)]

    # Wrap any iterable with progress tracking
    for item in oven.progress(data, desc='Processing items'):
        # Simulate processing
        time.sleep(0.1)
        # You can add custom logic here
        if random.random() < 0.1:  # 10% chance
            print(f'\nSpecial processing for {item}')

    print('Iterable progress completed!\n')


def example_manual_progress():
    """Manual progress updates."""
    print('=== Manual Progress Example ===')

    # Create progress bar with known total
    with oven.ProgressBar(total=200, desc='Manual updates') as pbar:
        for i in range(10):
            # Simulate batch processing
            batch_size = random.randint(15, 25)
            time.sleep(0.2)

            # Update progress manually
            pbar.update(batch_size)
            pbar.set_postfix(batch=i + 1, items_processed=pbar.n)

    print('Manual progress completed!\n')


def example_http_mode():
    """Progress with HTTP-based notifications (time intervals)."""
    print('=== HTTP Mode Progress (Time-based notifications) ===')

    # HTTP mode sends notifications at regular time intervals
    for i in oven.progress_range(
        100,
        desc='HTTP Mode Progress',
        notify_mode='http',
        notify_interval=5.0,  # Notify every 5 seconds
        notify_threshold=0.1,  # Or when 10% progress is made
    ):
        time.sleep(0.2)  # Simulate longer work

    print('HTTP mode progress completed!\n')


def example_socket_mode():
    """Progress with socket-based notifications (trigger-based)."""
    print('=== Socket Mode Progress (Trigger-based notifications) ===')

    # Socket mode sends notifications on manual triggers
    with oven.ProgressBar(
        total=50,
        desc='Socket Mode Progress',
        notify_mode='socket',
        notify_threshold=0.2,  # Notify on 20% progress changes
    ) as pbar:

        for i in range(50):
            time.sleep(0.1)
            pbar.update(1)

            # Notifications are sent automatically based on threshold
            # or you can force them by calling update()

    print('Socket mode progress completed!\n')


def example_disabled_notifications():
    """Progress bar without notifications (pure tqdm-like behavior)."""
    print('=== Progress Without Notifications ===')

    # Disable notifications to use as pure progress bar
    for i in oven.progress_range(
        30, desc='No notifications', enable_notifications=False
    ):
        time.sleep(0.1)

    print('Progress without notifications completed!\n')


def example_nested_progress():
    """Example with nested progress bars."""
    print('=== Nested Progress Example ===')

    # Outer progress for main tasks
    main_tasks = ['Task A', 'Task B', 'Task C']

    for task in oven.progress(main_tasks, desc='Main tasks'):
        print(f'\nStarting {task}')

        # Inner progress for subtasks
        subtasks = range(20)
        for subtask in oven.progress(
            subtasks,
            desc=f'  {task} subtasks',
            notify_interval=10.0,  # Less frequent notifications for subtasks
            leave=False,  # Don't leave progress bar after completion
        ):
            time.sleep(0.05)

        print(f'Completed {task}')

    print('Nested progress completed!\n')


def example_error_handling():
    """Example showing error handling in progress bars."""
    print('=== Error Handling Example ===')

    try:
        with oven.ProgressBar(total=50, desc='Error handling demo') as pbar:
            for i in range(50):
                time.sleep(0.05)
                pbar.update(1)

                # Simulate an error partway through
                if i == 30:
                    raise ValueError('Simulated error during processing')

    except ValueError as e:
        print(f'Caught error: {e}')
        print('Progress bar automatically sent error notification')

    print('Error handling example completed!\n')


def example_custom_formatting():
    """Example with custom progress formatting."""
    print('=== Custom Formatting Example ===')

    # Progress with custom description updates
    with oven.ProgressBar(total=100, desc='Custom formatting') as pbar:
        for i in range(100):
            time.sleep(0.03)

            # Update description dynamically
            if i < 25:
                pbar.set_description('Phase 1: Initialization')
            elif i < 50:
                pbar.set_description('Phase 2: Processing')
            elif i < 75:
                pbar.set_description('Phase 3: Analysis')
            else:
                pbar.set_description('Phase 4: Finalization')

            # Update postfix with current metrics
            pbar.set_postfix(
                phase=f'{i//25 + 1}/4',
                memory_usage=f'{random.randint(50, 100)}MB',
                cpu_usage=f'{random.randint(20, 80)}%',
            )

            pbar.update(1)

    print('Custom formatting example completed!\n')


if __name__ == '__main__':
    print('ExpOven Progress Notification Examples')
    print('=' * 50)
    print()

    # Run all examples
    example_basic_progress()
    example_iterable_progress()
    example_manual_progress()
    example_http_mode()
    example_socket_mode()
    example_disabled_notifications()
    example_nested_progress()
    example_error_handling()
    example_custom_formatting()

    print('All examples completed!')
    print('\nNote: To see notifications in messaging apps, make sure you have')
    print(
        'configured ExpOven with your preferred backend (DingTalk, Feishu, Email, etc.)'
    )
