# Adjust Client Library

The Adjust Client Library is a Python library for sending events to Adjust using the HTTP API. It includes functionality for validation, error handling, and retry mechanisms.

## Installation

The Adjust Client Library is available on PyPI. You can install it using pip or poetry:

```bash
pip install adjust-client
```

```bash 
poetry add adjust-client
```

## Usage

To use the Adjust Client Library, you need to create an instance of the `AdjustClient` class. You can then use the `send_event` method to send events to Adjust.

```python
from adjust_client import AdjustClientConfig, AdjustClient
config = AdjustClientConfig(app_token='your_app_token')

event_data = {
    'idfa': 'D2CADB5F-410F-4963-AC0C-2A78534BDF1E',
    'adid': 'test_adid',
    'ip_address': '192.168.0.1',
    'created_at_unix': 1625077800,
    'created_at': '2021-06-30T12:30:00Z'
}
client = AdjustClient(config)
await client.send_event(event_data)
```