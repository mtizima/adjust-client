import json

import httpx
from pydantic import BaseModel, model_validator, IPvAnyAddress, field_serializer
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from adjust_client import exceptions as client_exc
from adjust_client.config import AdjustClientConfig


class EventData(BaseModel):
    idfa: str | None = None
    gps_adid: str | None = None
    adid: str | None = None
    ip_address: IPvAnyAddress | None = None
    created_at_unix: int | None = None
    created_at: str | None = None
    callback_params: dict[str, str] | None = None

    @field_serializer('callback_params')
    def serialize_callback_params(self, value: dict | None, _info):
        """For detail refer to
        [Share custom data](https://dev.adjust.com/en/api/s2s-api/events#share-custom-data)
        """
        if value is None:
            return None
        return json.dumps(value, separators=(',', ':'))

    @model_validator(mode="before")
    def check_idfa_or_gps_adid(cls, values):
        idfa, gps_adid = values.get('idfa'), values.get('gps_adid')
        if not idfa and not gps_adid:
            raise ValueError('Either idfa or gps_adid must be provided')
        return values

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        if result.get("idfa") is not None:
            result.pop('gps_adid')
        if result.get("gps_adid") is not None:
            result.pop("idfa")
        return result


class AdjustClient:
    def __init__(self, config: AdjustClientConfig):
        self.config = config

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(client_exc.InternalServerError)
    )
    async def send_event(self, event_token: str, event_data: dict):
        valid_event_data = EventData(**event_data)
        params = {
            'app_token': self.config.app_token,
            'event_token': event_token,
            's2s': 1,
            **valid_event_data.dict()
        }

        headers = {'Authorization': f'Bearer {self.config.security_token}'} if self.config.security_token else {}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.config.base_url, params=params, headers=headers)
            self.handle_response(response)

        return response.json()

    def handle_response(self, response):
        if response.status_code == 200:
            return

        exceptions = {
            400: client_exc.BadEventStateError,
            401: client_exc.AuthorizationError,
            403: client_exc.AppInactiveError,
            404: client_exc.AppTokenNotFoundError,
            413: client_exc.RequestSizeTooLargeError,
            451: client_exc.DeviceOptedOutError,
            500: client_exc.InternalServerError
        }

        exception = exceptions.get(response.status_code)
        if exception:
            raise exception(response.text)

        response.raise_for_status()
