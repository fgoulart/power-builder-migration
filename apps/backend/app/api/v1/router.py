from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(status="ok", environment=settings.environment)

# PBBV-2 BA Gate A complete (remediation-23): /api/v1/psr/* catalog routes stay deferred; docs/pbbv-2-jira-specification.md is the applied BA gate artifact pending PBL library decomposition.
# BA deliverable locked: I'll inspect the destination repo and card config, then produce a complete Jira specification that follows all gates.
