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
    migration_inventory_root: str | None = None
    validate_modules_on_startup: bool = False

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
        if self.migration_inventory_root:
            return Path(self.migration_inventory_root).expanduser().resolve()
        repo_root = Path(__file__).resolve().parents[4]
        return (repo_root / "migration" / "origin-inventory").resolve()

    @property
    def runtime_liblist_path(self) -> Path:
        return self.resolved_migration_inventory_root / "runtime-liblist.json"

    @property
    def build_exlist_path(self) -> Path:
        return self.resolved_migration_inventory_root / "build-exlist.json"

    @property
    def library_manifest_path(self) -> Path:
        return self.resolved_migration_inventory_root / "library-manifest.yaml"

    @property
    def dependency_graph_path(self) -> Path:
        return self.resolved_migration_inventory_root / "dependency-graph.json"


settings = Settings()
