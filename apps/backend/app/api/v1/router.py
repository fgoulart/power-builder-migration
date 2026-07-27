from fastapi import APIRouter

from app.core.config import (
    get_build_only_modules,
    get_runtime_modules,
    settings,
    validate_runtime_resolution,
)
from app.schemas.health import HealthResponse, ModuleInfo, ModulesResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment)


@router.get("/modules", response_model=ModulesResponse)
def list_modules() -> ModulesResponse:
    """Diagnostic endpoint mirroring PowerBuilder LibList / EXLIST resolution."""
    report = validate_runtime_resolution()
    runtime_modules = [
        ModuleInfo(
            id=module.id,
            pbl=module.pbl,
            status=module.status,
            load_order=module.load_order,
        )
        for module in get_runtime_modules()
    ]
    build_only_modules = [
        ModuleInfo(
            id=module.id,
            pbl=module.pbl,
            status=module.status,
            load_order=module.load_order,
        )
        for module in get_build_only_modules()
    ]
    return ModulesResponse(
        runtime_modules=runtime_modules,
        build_only_modules=build_only_modules,
        resolution_ok=report.ok,
        errors=report.errors,
    )
