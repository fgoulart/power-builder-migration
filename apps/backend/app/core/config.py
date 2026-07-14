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
    public_api_url: str = "http://localhost:8000"
    bind_host: str = "0.0.0.0"
    bind_port: int = 8000
    https_enabled: bool = False
    session_timeout_seconds: int = 3600
    request_timeout_seconds: int = 3600
    transaction_timeout_seconds: int = 120
    license_required: bool = False
    appeon_license_key: str | None = None
    license_key: str | None = None
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


settings = Settings()
