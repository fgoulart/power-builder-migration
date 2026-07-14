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
    # PBBV-2 BA: sequence step 1 copies 12 golden PSR binaries from PSR_ORIGIN_PATH into fixtures/psr/golden.
    psr_origin_path: str = "/workspace/PowerBuilder-Example"
    psr_golden_expected_count: int = 12
    psr_golden_expected_total_bytes: int = 395_785
    # PBBV-2 Gate A: QT_CARDS=1 — single modernization card for destination-only PSR fixture pipeline.
    psr_qt_cards: int = 1
    psr_jira_issue_key: str = "PBBV-2"
    psr_affected_source_id: str = "66704f36-a39a-4b8d-8c82-79cd02f1b9c6"

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
    def resolved_psr_origin_path(self) -> Path:
        return Path(self.psr_origin_path).expanduser().resolve()

    @property
    def psr_manifest_path(self) -> Path:
        return self.psr_metadata_dir / "manifest.json"

settings = Settings()
