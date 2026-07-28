from fastapi import APIRouter

from app.core.config import validate_runtime_resolution
from app.schemas.health import HealthResponse, ModulesResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(status="ok", environment=settings.environment)


@router.get("/modules", response_model=ModulesResponse)
def list_modules() -> ModulesResponse:
    report = validate_runtime_resolution()
    return ModulesResponse.model_validate(report)
