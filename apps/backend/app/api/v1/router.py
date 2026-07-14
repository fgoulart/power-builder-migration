from fastapi import APIRouter

from app.api.v1.psr import router as psr_router
from app.schemas.health import HealthResponse

router = APIRouter()
router.include_router(psr_router)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(status="ok", environment=settings.environment)
