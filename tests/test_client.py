from unittest.mock import patch

import httpx
import pytest
from pydantic import ValidationError

from adjust_client import exceptions as client_exc
from adjust_client.client import AdjustClient
from adjust_client.config import AdjustClientConfig


@pytest.fixture
def config():
    return AdjustClientConfig(app_token='YOUR_APP_TOKEN', security_token='YOUR_SECURITY_TOKEN')


@pytest.fixture
def client(config):
    return AdjustClient(config=config)


@pytest.mark.asyncio
async def test_send_event_with_valid_data(client):
    event_data = {
        'idfa': 'D2CADB5F-410F-4963-AC0C-2A78534BDF1E',
        'adid': 'test_adid',
        'ip_address': '192.168.0.1',
        'created_at_unix': 1625077800,
        'created_at': '2021-06-30T12:30:00Z'
    }
    event_token = 'valid_event_token'

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = httpx.Response(status_code=200, json={'success': True})
        mock_get.return_value = mock_response

        response = await client.send_event(event_token, event_data)
        assert response == {'success': True}


@pytest.mark.asyncio
async def test_send_event_without_idfa_or_gps_adid(client):
    event_data = {
        'adid': 'test_adid',
        'ip_address': '192.168.0.1',
        'created_at_unix': 1625077800,
        'created_at': '2021-06-30T12:30:00Z'
    }
    event_token = 'valid_event_token'

    with pytest.raises(ValidationError):
        await client.send_event(event_token, event_data)


@pytest.mark.asyncio
async def test_handle_400_error(client):
    event_data = {
        'idfa': 'D2CADB5F-410F-4963-AC0C-2A78534BDF1E',
        'adid': 'test_adid',
        'ip_address': '192.168.0.1',
        'created_at_unix': 1625077800,
        'created_at': '2021-06-30T12:30:00Z'
    }
    event_token = 'valid_event_token'

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = httpx.Response(status_code=400, text='Bad event state')
        mock_get.return_value = mock_response

        with pytest.raises(client_exc.BadEventStateError):
            await client.send_event(event_token, event_data)


@pytest.mark.asyncio
async def test_handle_500_error_with_retry(client):
    event_data = {
        'idfa': 'D2CADB5F-410F-4963-AC0C-2A78534BDF1E',
        'gps_adid': 'test_adid',
        'ip_address': '192.168.0.1',
        'created_at_unix': 1625077800,
        'created_at': '2021-06-30T12:30:00Z'
    }
    event_token = 'valid_event_token'

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response_500 = httpx.Response(status_code=500, text='Internal error')
        mock_response_200 = httpx.Response(status_code=200, json={'success': True})
        mock_get.side_effect = [mock_response_500, mock_response_500, mock_response_200]

        response = await client.send_event(event_token, event_data)
        assert response == {'success': True}
