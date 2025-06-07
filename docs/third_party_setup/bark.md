# Bark Notification Backend Setup

This guide explains how to configure ExpOven to send notifications via [Bark](https://github.com/Finb/Bark), an open-source notification service for iOS devices.

## Prerequisites

1. A Bark server (self-hosted or using the [public instance](https://api.day.app)).
2. A device key from your Bark app.
3. ExpOven installed (`pip install ExpOven`).

## Configuration

### 1. Get Your Bark Device Key
- Install the Bark app on your iOS device.
- Open the app and note your device key (e.g., `https://api.day.app/abcdef123456`).

### 2. Minimal Configuration
Add the following to your `config.yaml`:

```yaml
backend: bark
bark:
  base_url: "https://api.day.app/YOUR_DEVICE_KEY"  # Replace with your device key
```

### 3. Advanced Configuration
Below is an example of all available parameters for the Bark backend:

```yaml
backend: bark
bark:
  base_url: "https://api.day.app/YOUR_DEVICE_KEY"  # Replace with your device key
  default_params:  # Optional defaults for all notifications
    sound: "alarm"
    icon: "https://example.com/icon.png"
    group: "experiments"
    auto_copy: true
```

#### Parameter Reference

| Parameter  | Type | Default        | Description                              |
|------------|------|----------------|------------------------------------------|
| content    | str  | Required       | Main notification text                   |
| title      | str  | "ExpOven Notification" | Notification title                |
| sound      | str  | None           | Alert sound (e.g., "alarm", "bell")      |
| icon       | str  | None           | URL for notification icon                |
| group      | str  | None           | Notification group name                  |
| level      | str  | None           | Priority ("active", "timeSensitive", "passive") |
| url        | str  | None           | URL to open when tapped                  |
| badge      | int  | None           | Badge number to display                  |
| auto_copy  | bool | True           | Auto-copy content to clipboard           |
| copy_text  | str  | None           | Custom text to copy instead of content   |

---

### Notes
- Ensure the `config.yaml` file is saved in the correct directory (typically the root of your ExpOven project).
- Run `blue .` in the `ExpOven` directory to format all Python files before creating the pull request.
- Verify the Bark `base_url` includes your actual device key to avoid notification failures.
