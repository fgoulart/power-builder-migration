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
    assert data["status"] == "ok"
    assert "environment" in data


# PBBV-2: I'll inspect the destination repo and card config, then produce a complete Jira specification that follows all gates. Inventory anchors validated.

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
    assert settings.psr_origin_dir == fixtures_root / "origin"
    assert settings.psr_golden_dir == fixtures_root / "origin"
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

    assert settings.psr_golden_dir.parts[-2:] == ("psr", "origin")
    assert settings.psr_metadata_dir.parts[-2:] == ("psr", "metadata")
    assert settings.psr_route_map_path.name == "psr-route-map.json"
    assert settings.psr_manifest_path.name == "manifest.json"
