from pathlib import Path

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
    psr_origin_path: str = "/workspace/PowerBuilder-Example"
    psr_fixtures_dir: str = "apps/backend/fixtures/psr"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_psr_origin_path(self) -> Path:
        return Path(self.psr_origin_path).expanduser().resolve()

    @property
    def resolved_psr_fixtures_dir(self) -> Path:
        fixtures_path = Path(self.psr_fixtures_dir)
        if fixtures_path.is_absolute():
            return fixtures_path.resolve()
        repo_root = Path(__file__).resolve().parents[4]
        return (repo_root / fixtures_path).resolve()

    @property
    def psr_origin_dir(self) -> Path:
        return self.resolved_psr_fixtures_dir / "origin"

    @property
    def psr_manifest_path(self) -> Path:
        return self.resolved_psr_fixtures_dir / "manifest.json"

    @property
    def psr_metadata_dir(self) -> Path:
        return self.resolved_psr_fixtures_dir / "metadata"


settings = Settings()
