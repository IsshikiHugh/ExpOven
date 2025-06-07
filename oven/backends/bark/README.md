# ExpOven - Bark Notification Backend
## Usage

1. Install dependencies:
```bash
pip install ExpOven
```

2. Configure Bark backend in `cfg.yaml` as shown above.

3. Send a notification:

```python
from oven.backends.bark import BarkBackendInfo

# Initialize the Bark backend
bark = BarkBackendInfo(
    api_key="YOUR_DEVICE_KEY",
    base_url="https://api.day.app"
)

# Send a notification
bark.notify(
    content="Experiment completed!",
    title="ExpOven Alert",
    sound="bell",
    group="experiments"
)
```



## Testing

Unit tests are available to verify the Bark backend functionality:

1. Navigate to the project root:
```bash
cd ExpOven
```

2. Format code (optional):
```bash
blue .
```

3. Run tests:
```bash
python -m unittest tests/test_bark_backend.py
```

### Test Cases

- **Basic Notification**: Verifies correct URL construction and successful response handling
- **Notification with Parameters**: Tests additional parameters (sound, group, etc.)
- **Failed Notification**: Simulates and handles failed requests

## Notes

- Ensure `cfg.yaml` is in the project root or your specified configuration directory
- For self-hosted Bark servers, update the `base_url` in your configuration
- The backend requires internet access to communicate with the Bark server
```
