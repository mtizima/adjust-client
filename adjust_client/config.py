from pydantic import BaseModel, Field, HttpUrl


class AdjustClientConfig(BaseModel):
    app_token: str
    environment: str = 'production'
    base_url: HttpUrl = 'https://s2s.adjust.com/event'
    security_token: str | None = None
