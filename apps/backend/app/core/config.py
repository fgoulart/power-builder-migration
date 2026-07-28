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

    @property
    def resolved_migration_inventory_root(self) -> Path:
        repo_root = Path(__file__).resolve().parents[4]
        return (repo_root / "migration" / "origin-inventory").resolve()

    @property
    def runtime_liblist_path(self) -> Path:
        return self.resolved_migration_inventory_root / "runtime-liblist.json"

    @property
    def build_exlist_path(self) -> Path:
        return self.resolved_migration_inventory_root / "build-exlist.json"


# Canonical runtime LibList order from origin PB Examples.pbt (10 libraries).
RUNTIME_MODULE_CATALOG: tuple[dict[str, object], ...] = (
    {"id": "shell", "pbl": "pbexamfe", "load_order": 1, "prefix": "fe"},
    {"id": "datawindows-d1", "pbl": "pbexamd1", "load_order": 2, "prefix": "d1"},
    {"id": "datawindows-d2", "pbl": "pbexamd2", "load_order": 3, "prefix": "d2"},
    {"id": "shared", "pbl": "pbexamfn", "load_order": 4, "prefix": "fn"},
    {"id": "layout", "pbl": "pbexammn", "load_order": 5, "prefix": "mn"},
    {"id": "system", "pbl": "pbexamsy", "load_order": 6, "prefix": "sy"},
    {"id": "shared-components", "pbl": "pbexamuo", "load_order": 7, "prefix": "uo"},
    {"id": "windows-w1", "pbl": "pbexamw1", "load_order": 8, "prefix": "w1"},
    {"id": "windows-w2", "pbl": "pbexamw2", "load_order": 9, "prefix": "w2"},
    {"id": "windows-w3", "pbl": "pbexamw3", "load_order": 10, "prefix": "w3"},
)

# WIN32 EXLIST build-only libraries (excluded from runtime resolution).
BUILD_ONLY_MODULE_CATALOG: tuple[dict[str, object], ...] = (
    {"id": "stored-procedures", "pbl": "pbexamsa", "load_order": 6, "prefix": "sa"},
    {"id": "orca-xref", "pbl": "pbexamor", "load_order": 8, "prefix": "or"},
)

EXPECTED_RUNTIME_LIBLIST: tuple[str, ...] = tuple(
    str(entry["pbl"]) for entry in RUNTIME_MODULE_CATALOG
)
EXPECTED_BUILD_EXLIST: tuple[str, ...] = (
    "pbexamfe",
    "pbexamd1",
    "pbexamd2",
    "pbexamfn",
    "pbexammn",
    "pbexamsa",
    "pbexamsy",
    "pbexamor",
    "pbexamuo",
    "pbexamw1",
    "pbexamw2",
    "pbexamw3",
)


def get_runtime_modules() -> list[dict[str, object]]:
    return [
        {
            "id": entry["id"],
            "pbl": entry["pbl"],
            "status": "resolved",
            "load_order": entry["load_order"],
        }
        for entry in RUNTIME_MODULE_CATALOG
    ]


def get_build_only_modules() -> list[dict[str, object]]:
    return [
        {
            "id": entry["id"],
            "pbl": entry["pbl"],
            "status": "resolved",
            "load_order": entry["load_order"],
        }
        for entry in BUILD_ONLY_MODULE_CATALOG
    ]


def validate_runtime_resolution() -> dict[str, object]:
    errors: list[str] = []
    runtime_modules = get_runtime_modules()
    if len(runtime_modules) != 10:
        errors.append(f"expected 10 runtime_modules, found {len(runtime_modules)}")
    ordered_pbls = [str(item["pbl"]) for item in runtime_modules]
    if ordered_pbls != list(EXPECTED_RUNTIME_LIBLIST):
        errors.append("runtime_modules load_order does not match origin LibList")
    build_only_pbls = {str(item["pbl"]) for item in get_build_only_modules()}
    if "pbexamsa" not in build_only_pbls:
        errors.append("build_only_modules missing pbexamsa (stored-procedures)")
    if any(str(item["pbl"]) in build_only_pbls for item in runtime_modules):
        errors.append("build-only libraries must be excluded from runtime_modules")
    return {
        "runtime_modules": runtime_modules,
        "build_only_modules": get_build_only_modules(),
        "resolution_ok": len(errors) == 0,
        "errors": errors,
    }


settings = Settings()
