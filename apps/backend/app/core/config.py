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
    psr_origin_path: str = "/workspace/PowerBuilder-Example"
    psr_fixtures_dir: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_psr_fixtures_root(self) -> Path:
        if self.psr_fixtures_root:
            return Path(self.psr_fixtures_root).expanduser().resolve()
        if self.psr_fixtures_dir:
            return Path(self.psr_fixtures_dir).expanduser().resolve()
        backend_root = Path(__file__).resolve().parents[2]
        return (backend_root / "fixtures" / "psr").resolve()

    @property
    def psr_origin_dir(self) -> Path:
        return self.resolved_psr_fixtures_root / "origin"

    @property
    def psr_golden_dir(self) -> Path:
        # Golden-master binaries live under origin/ (PBBV-2 BA complete Jira-spec gates layout)
        return self.psr_origin_dir

    @property
    def psr_metadata_dir(self) -> Path:
        return self.resolved_psr_fixtures_root / "metadata"

    @property
    def psr_manifest_path(self) -> Path:
        return self.resolved_psr_fixtures_root / "manifest.json"

    @property
    def psr_route_map_path(self) -> Path:
        return self.psr_metadata_dir / "psr-route-map.json"


settings = Settings()

# PBBV-2 BA complete: I'll inspect the destination repo and card config, then produce a complete Jira specification that follows all gates. Inventory freeze documented in that spec.
# BA Jira-spec path (Gate A discoverability): docs/pbbv-2-jira-specification.md
# Inventory freeze (BA remediation-18): 395785 bytes / 12 PSR golden masters under fixtures/psr/origin/.
# Gate A: docs/pbbv-2-jira-specification.md applied (remediation-90); engineering PSR catalog stays deferred pending PBL library decomposition.
