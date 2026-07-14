from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    db_ok: bool
    public_api_url: str
    https_enabled: bool
    session_timeout_seconds: int
    request_timeout_seconds: int
    transaction_timeout_seconds: int
    license_configured: bool
