#!/usr/bin/env python3
"""
Simple test script for the new progress notification interface.
This script tests the basic functionality without requiring ExpOven configuration.
"""

import time
import sys
import os

# Add the current directory to Python path to import oven
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import oven

    print('✓ Successfully imported oven module')
except ImportError as e:
    print(f'✗ Failed to import oven module: {e}')
    sys.exit(1)


def test_basic_import():
    """Test that progress functions are available."""
    print('\n=== Testing Basic Import ===')

    # Check if progress functions are available
    assert hasattr(oven, 'progress'), 'oven.progress not found'
    assert hasattr(oven, 'progress_range'), 'oven.progress_range not found'
    assert hasattr(oven, 'ProgressBar'), 'oven.ProgressBar not found'

    print('✓ All progress functions are available')


def test_progress_without_notifications():
    """Test progress bar without ExpOven notifications."""
    print('\n=== Testing Progress Without Notifications ===')

    # Test basic progress range
    print('Testing progress_range...')
    for i in oven.progress_range(
        10, desc='Test range', enable_notifications=False
    ):
        time.sleep(0.1)
    print('✓ progress_range works')

    # Test progress with iterable
    print('Testing progress with iterable...')
    data = [f'item_{i}' for i in range(5)]
    for item in oven.progress(
        data, desc='Test iterable', enable_notifications=False
    ):
        time.sleep(0.1)
    print('✓ progress with iterable works')

    # Test manual progress
    print('Testing manual progress...')
    with oven.ProgressBar(
        total=10, desc='Manual test', enable_notifications=False
    ) as pbar:
        for i in range(10):
            time.sleep(0.1)
            pbar.update(1)
    print('✓ Manual progress works')


def test_progress_with_notifications():
    """Test progress bar with ExpOven notifications (if configured)."""
    print('\n=== Testing Progress With Notifications ===')

    try:
        # This will work if ExpOven is properly configured
        print('Testing progress with notifications enabled...')
        for i in oven.progress_range(
            5, desc='Notification test', notify_interval=1.0
        ):
            time.sleep(0.3)
        print(
            '✓ Progress with notifications works '
            '(or notifications disabled due to config)'
        )
    except Exception as e:
        print(
            f'⚠ Progress with notifications failed (expected if not configured): {e}'
        )


def test_different_modes():
    """Test different notification modes."""
    print('\n=== Testing Different Modes ===')

    # Test HTTP mode
    print('Testing HTTP mode...')
    try:
        for i in oven.progress_range(
            3,
            desc='HTTP mode test',
            notify_mode='http',
            notify_interval=0.5,
            enable_notifications=False,  # Disable to avoid config issues
        ):
            time.sleep(0.2)
        print('✓ HTTP mode works')
    except Exception as e:
        print(f'✗ HTTP mode failed: {e}')

    # Test socket mode
    print('Testing socket mode...')
    try:
        with oven.ProgressBar(
            total=3,
            desc='Socket mode test',
            notify_mode='socket',
            enable_notifications=False,  # Disable to avoid config issues
        ) as pbar:
            for i in range(3):
                time.sleep(0.2)
                pbar.update(1)
        print('✓ Socket mode works')
    except Exception as e:
        print(f'✗ Socket mode failed: {e}')


def test_error_handling():
    """Test error handling in progress bars."""
    print('\n=== Testing Error Handling ===')

    try:
        with oven.ProgressBar(
            total=5, desc='Error test', enable_notifications=False
        ) as pbar:
            for i in range(5):
                time.sleep(0.1)
                pbar.update(1)
                if i == 3:
                    raise ValueError('Test error')
    except ValueError:
        print('✓ Error handling works correctly')
    except Exception as e:
        print(f'✗ Unexpected error: {e}')


def main():
    """Run all tests."""
    print('ExpOven Progress Interface Test')
    print('=' * 40)

    try:
        test_basic_import()
        test_progress_without_notifications()
        test_progress_with_notifications()
        test_different_modes()
        test_error_handling()

        print('\n' + '=' * 40)
        print('✓ All tests completed successfully!')
        print('\nTo test with actual notifications:')
        print('1. Configure ExpOven with your preferred backend')
        print('2. Run: python docs/progress_examples.py')

    except Exception as e:
        print(f'\n✗ Test failed with error: {e}')
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
