from dataclasses import dataclass, field
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    environment: str = "development"
    debug: bool = True
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/power_builder"
    cors_origins: str = "http://localhost:4200"
    api_v1_prefix: str = "/api/v1"
    psr_fixtures_root: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


    @property
    def resolved_psr_fixtures_root(self) -> Path:
        if self.psr_fixtures_root:
            return Path(self.psr_fixtures_root).expanduser().resolve()
        repo_root = Path(__file__).resolve().parents[4]
        return (repo_root / "fixtures" / "psr").resolve()

    @property
    def psr_golden_dir(self) -> Path:
        return self.resolved_psr_fixtures_root / "golden"

    @property
    def psr_metadata_dir(self) -> Path:
        return self.resolved_psr_fixtures_root / "metadata"

    @property
    def psr_route_map_path(self) -> Path:
        return self.psr_metadata_dir / "psr-route-map.json"




@dataclass(frozen=True)
class ModuleDescriptor:
    """Modernization module descriptor mapped from a PowerBuilder PBL library."""

    id: str
    pbl: str
    load_order: int
    status: str = "resolved"


@dataclass
class ResolutionReport:
    """Result of validating runtime module resolution order."""

    ok: bool
    errors: list[str] = field(default_factory=list)


RUNTIME_MODULE_CATALOG: tuple[ModuleDescriptor, ...] = (
    ModuleDescriptor(id="shell", pbl="pbexamfe", load_order=1, status="resolved"),
    ModuleDescriptor(id="datawindows-d1", pbl="pbexamd1", load_order=2, status="resolved"),
    ModuleDescriptor(id="datawindows-d2", pbl="pbexamd2", load_order=3, status="resolved"),
    ModuleDescriptor(id="shared", pbl="pbexamfn", load_order=4, status="resolved"),
    ModuleDescriptor(id="layout", pbl="pbexammn", load_order=5, status="resolved"),
    ModuleDescriptor(id="system", pbl="pbexamsy", load_order=6, status="resolved"),
    ModuleDescriptor(id="shared-components", pbl="pbexamuo", load_order=7, status="resolved"),
    ModuleDescriptor(id="windows-w1", pbl="pbexamw1", load_order=8, status="resolved"),
    ModuleDescriptor(id="windows-w2", pbl="pbexamw2", load_order=9, status="resolved"),
    ModuleDescriptor(id="windows-w3", pbl="pbexamw3", load_order=10, status="resolved"),
)

BUILD_ONLY_MODULE_CATALOG: tuple[ModuleDescriptor, ...] = (
    ModuleDescriptor(id="stored-procedures", pbl="pbexamsa", load_order=6, status="resolved"),
    ModuleDescriptor(id="orca-xref", pbl="pbexamor", load_order=8, status="resolved"),
)

EXPECTED_RUNTIME_PBLS: tuple[str, ...] = (
    "pbexamfe",
    "pbexamd1",
    "pbexamd2",
    "pbexamfn",
    "pbexammn",
    "pbexamsy",
    "pbexamuo",
    "pbexamw1",
    "pbexamw2",
    "pbexamw3",
)


def get_runtime_modules() -> list[ModuleDescriptor]:
    """Return the 10 runtime modules in LibList order."""
    return list(RUNTIME_MODULE_CATALOG)


def get_build_only_modules() -> list[ModuleDescriptor]:
    """Return build-only modules (pbexamsa, pbexamor) excluded from runtime resolution."""
    return list(BUILD_ONLY_MODULE_CATALOG)


def validate_runtime_resolution() -> ResolutionReport:
    """Validate that all runtime modules resolve in LibList order with no gaps."""
    errors: list[str] = []
    modules = get_runtime_modules()

    if len(modules) != 10:
        errors.append(f"expected 10 runtime modules, found {len(modules)}")

    ordered = sorted(modules, key=lambda m: m.load_order)
    for index, module in enumerate(ordered, start=1):
        if module.load_order != index:
            errors.append(
                f"load_order gap at position {index}: got {module.load_order} for {module.pbl}"
            )
        if module.status != "resolved":
            errors.append(f"module {module.id} ({module.pbl}) status is {module.status}")

    actual_pbls = tuple(m.pbl for m in ordered)
    if actual_pbls != EXPECTED_RUNTIME_PBLS:
        errors.append(
            "runtime PBL order does not match origin LibList: "
            f"expected {EXPECTED_RUNTIME_PBLS}, got {actual_pbls}"
        )

    build_only_pbls = {m.pbl for m in get_build_only_modules()}
    for pbl in ("pbexamsa", "pbexamor"):
        if pbl not in build_only_pbls:
            errors.append(f"build-only PBL {pbl} missing from build_only catalog")
        if pbl in actual_pbls:
            errors.append(f"build-only PBL {pbl} must not appear in runtime modules")

    return ResolutionReport(ok=len(errors) == 0, errors=errors)


settings = Settings()
