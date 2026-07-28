from fastapi import APIRouter

from app.api.v1.modules_router import router as modules_router
from app.schemas.health import HealthResponse

router = APIRouter()
router.include_router(modules_router)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(status="ok", environment=settings.environment)
