# Bark Notification Backend Setup

This guide explains how to configure ExpOven to send notifications via [Bark](https://github.com/Finb/Bark), an open-source notification service for iOS devices.

## Prerequisites

1. A Bark server (self-hosted or using the [public instance](https://api.day.app))
2. Device key from your Bark app
3. ExpOven installed (`pip install ExpOven`)

## Configuration

### 1. Get Your Bark Device Key
- Install the Bark app on your iOS device
- Open the app and note your device key (looks like `https://api.day.app/abcdef123456`)

### 2. Minimal Configuration
Add to your `config.yaml`:

```yaml
backend: bark
bark:
  base_url: "https://api.day.app/YOUR_DEVICE_KEY"  # Replace with your key


Advanced Configuration
All available parameters:

yaml
backend: bark
bark:
  base_url: "https://api.day.app/YOUR_DEVICE_KEY"
  default_params:  # Optional defaults for all notifications
    sound: "alarm"
    icon: "https://example.com/icon.png"
    group: "experiments"
    auto_copy: true



Parameter  Type	    Default	      Description
content	   str	    Required	Main notification text
title	   str	    ExpOven     Notification	Notification title
sound	   str	    None	    Alert sound (e.g., "alarm", "bell")
icon	   str	    None	    URL for notification icon
group	   str	    None	    Notification group name
level	   str	    None	    Priority ("active", "timeSensitive", "passive")
url	       str	    None	    URL to open when tapped
badge	   int	    None	    Badge number to display
auto_copy  bool	    True	    Auto-copy content to clipboard
copy_text  str	    None	    Custom text to copy instead of content