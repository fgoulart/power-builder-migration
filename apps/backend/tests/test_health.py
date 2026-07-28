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


def test_get_modules_returns_200() -> None:
    response = client.get("/api/v1/modules")
    assert response.status_code == 200


def test_get_modules_resolution_ok_true() -> None:
    response = client.get("/api/v1/modules")
    data = response.json()
    assert data["resolution_ok"] is True
    assert data["errors"] == []


def test_modules_runtime_contract_matches_liblist() -> None:
    response = client.get("/api/v1/modules")
    data = response.json()
    runtime_modules = data["runtime_modules"]
    assert len(runtime_modules) == 10
    assert runtime_modules[0]["pbl"] == "pbexamfe"
    assert runtime_modules[0]["status"] == "resolved"
    assert runtime_modules[0]["load_order"] == 1
    assert [module["load_order"] for module in runtime_modules] == list(range(1, 11))


def test_modules_build_only_excludes_stored_procedures_from_runtime() -> None:
    response = client.get("/api/v1/modules")
    data = response.json()
    build_only_modules = data["build_only_modules"]
    runtime_pbls = {module["pbl"] for module in data["runtime_modules"]}
    assert any(
        module["id"] == "stored-procedures" and module["pbl"] == "pbexamsa"
        for module in build_only_modules
    )
    assert "pbexamsa" not in runtime_pbls
    assert "pbexamor" not in runtime_pbls
