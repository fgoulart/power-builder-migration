from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(status="ok", environment=settings.environment)

# PBBV-2 BA Gate A (remediation-4): /api/v1/psr/* catalog routes stay deferred until docs/pbbv-2-jira-specification.md is accepted and the PBL library decomposition blocker clears.
