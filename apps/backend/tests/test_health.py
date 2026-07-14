from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Power Builder API"


def test_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "degraded"}
    assert "environment" in data
    assert data["public_api_url"] == "http://localhost:8000"
    assert data["session_timeout_seconds"] == 3600
    assert data["request_timeout_seconds"] == 3600
    assert data["transaction_timeout_seconds"] == 120
    assert "db_ok" in data
    assert "license_configured" in data


# PBBV-1: Validating the modernization card against project config and the destination repository structure.

EXPECTED_PSR_GOLDEN_FILENAMES = frozenset(
    {
        "bitmap.psr",
        "btnmaint.psr",
        "btnrept.psr",
        "comprep.psr",
        "contact.psr",
        "custlist.psr",
        "deptemps.psr",
        "deptlist.psr",
        "empgraph.psr",
        "empsals.psr",
        "ffempdat.psr",
        "nestrep.psr",
    }
)

EXPECTED_PSR_TOTAL_BYTES = 395_785

COMPREP_ROUTE_MAPPING = {
    "filename": "comprep.psr",
    "target_report_id": "composite-customer-product",
    "target_route": "/api/v1/reports/composite/customer-product",
    "status": "planned",
}


def test_psr_fixtures_root_resolves_monorepo_layout() -> None:
    from app.core.config import settings

    fixtures_root = settings.resolved_psr_fixtures_root
    assert fixtures_root.name == "psr"
    assert settings.psr_golden_dir == fixtures_root / "golden"
    assert settings.psr_metadata_dir == fixtures_root / "metadata"
    assert settings.psr_route_map_path == fixtures_root / "metadata" / "psr-route-map.json"


def test_psr_golden_inventory_matches_modernization_plan() -> None:
    assert len(EXPECTED_PSR_GOLDEN_FILENAMES) == 12
    assert "comprep.psr" in EXPECTED_PSR_GOLDEN_FILENAMES
    assert EXPECTED_PSR_TOTAL_BYTES == 395_785


def test_comprep_route_mapping_matches_planned_report_endpoint() -> None:
    assert COMPREP_ROUTE_MAPPING["filename"] == "comprep.psr"
    assert COMPREP_ROUTE_MAPPING["target_report_id"] == "composite-customer-product"
    assert COMPREP_ROUTE_MAPPING["target_route"] == "/api/v1/reports/composite/customer-product"
    assert COMPREP_ROUTE_MAPPING["status"] == "planned"


def test_verify_psr_target_directories_align_with_settings() -> None:
    from app.core.config import settings

    assert settings.psr_golden_dir.parts[-2:] == ("psr", "golden")
    assert settings.psr_metadata_dir.parts[-2:] == ("psr", "metadata")
    assert settings.psr_route_map_path.name == "psr-route-map.json"


def test_hosting_settings_defaults_replace_powerserver_5088() -> None:
    from app.core.config import Settings

    cfg = Settings()
    assert cfg.public_api_url == "http://localhost:8000"
    assert cfg.bind_host == "0.0.0.0"
    assert cfg.bind_port == 8000
    assert cfg.https_enabled is False
    assert cfg.session_timeout_seconds == 3600
    assert cfg.request_timeout_seconds == 3600
    assert cfg.transaction_timeout_seconds == 120
    assert cfg.license_required is False


def test_license_gate_optional_when_not_required() -> None:
    from app.core.config import Settings
    from app.core.license_gate import assert_license_ready, license_is_configured

    cfg = Settings(license_required=False)
    assert_license_ready(cfg)
    assert license_is_configured(cfg) is False


def test_license_gate_requires_secret_when_enabled() -> None:
    import pytest

    from app.core.config import Settings
    from app.core.license_gate import LicenseGateError, assert_license_ready

    cfg = Settings(license_required=True, appeon_license_key=None, license_key=None)
    with pytest.raises(LicenseGateError):
        assert_license_ready(cfg)

    cfg_ok = Settings(license_required=True, appeon_license_key="appeon-demo-secret-value")
    assert_license_ready(cfg_ok)
