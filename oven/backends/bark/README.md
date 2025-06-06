# Bark Notification Backend

## Setup
1. Install the Bark app on your iOS device
2. Get your device key from the app
3. Configure in `cfg.yaml`:

```yaml
backends:
  bark:
    api_key: "YOUR_DEVICE_KEY"
    # Optional:
    base_url: "https://api.day.app"  # For self-hosted servers


## Bark Backend

To use the Bark notification backend:

1. Install required dependencies (if any)
2. Configure your Bark server URL in settings
3. Create a Bark notification:

```python
from oven.backends.bark import BarkBackendInfo
