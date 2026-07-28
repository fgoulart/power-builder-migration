from fastapi import APIRouter

from app.schemas.health import HealthResponse, ModuleInfo, ModulesResponse

router = APIRouter()

# Runtime LibList order from origin PB Examples.pbt (10 libraries).
_RUNTIME_MODULE_SPECS: tuple[tuple[str, str, int], ...] = (
    ("shell", "pbexamfe", 1),
    ("datawindows-d1", "pbexamd1", 2),
    ("datawindows-d2", "pbexamd2", 3),
    ("shared", "pbexamfn", 4),
    ("layout", "pbexammn", 5),
    ("system", "pbexamsy", 6),
    ("shared-components", "pbexamuo", 7),
    ("windows-w1", "pbexamw1", 8),
    ("windows-w2", "pbexamw2", 9),
    ("windows-w3", "pbexamw3", 10),
)

# Build-only libraries from exam.dat WIN32 EXLIST (excluded from runtime resolution).
_BUILD_ONLY_MODULE_SPECS: tuple[tuple[str, str, int], ...] = (
    ("stored-procedures", "pbexamsa", 6),
    ("orca-xref", "pbexamor", 8),
)


def _as_module_info(module_id: str, pbl: str, load_order: int, status: str = "resolved") -> ModuleInfo:
    return ModuleInfo(id=module_id, pbl=pbl, status=status, load_order=load_order)


def get_runtime_modules() -> list[ModuleInfo]:
    return [
        _as_module_info(module_id, pbl, load_order)
        for module_id, pbl, load_order in _RUNTIME_MODULE_SPECS
    ]


def get_build_only_modules() -> list[ModuleInfo]:
    return [
        _as_module_info(module_id, pbl, load_order)
        for module_id, pbl, load_order in _BUILD_ONLY_MODULE_SPECS
    ]


def validate_runtime_resolution() -> ModulesResponse:
    runtime_modules = get_runtime_modules()
    build_only_modules = get_build_only_modules()
    errors: list[str] = []

    if len(runtime_modules) != 10:
        errors.append(f"expected 10 runtime_modules, found {len(runtime_modules)}")

    expected_pbls = [pbl for _, pbl, _ in _RUNTIME_MODULE_SPECS]
    actual_pbls = [module.pbl for module in runtime_modules]
    if actual_pbls != expected_pbls:
        errors.append("runtime_modules load_order does not match origin LibList")

    build_only_pbls = {module.pbl for module in build_only_modules}
    if "pbexamsa" not in build_only_pbls:
        errors.append("build_only_modules missing pbexamsa (stored-procedures)")
    if any(module.pbl in build_only_pbls for module in runtime_modules):
        errors.append("build-only PBLs must be excluded from runtime_modules")

    for module in runtime_modules:
        if module.status != "resolved":
            errors.append(f"module {module.pbl} is not resolved")

    return ModulesResponse(
        runtime_modules=runtime_modules,
        build_only_modules=build_only_modules,
        resolution_ok=not errors,
        errors=errors,
    )


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(status="ok", environment=settings.environment)


@router.get("/modules", response_model=ModulesResponse)
def list_modules() -> ModulesResponse:
    """Diagnostic endpoint mirroring PowerBuilder LibList / EXLIST resolution."""
    return validate_runtime_resolution()
