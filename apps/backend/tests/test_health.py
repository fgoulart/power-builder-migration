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

# PBBV-6: Module registry mirrors origin LibList / EXLIST resolution.

EXPECTED_RUNTIME_PBLS = (
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

EXPECTED_BUILD_ONLY_PBLS = ("pbexamsa", "pbexamor")


def test_modules_endpoint_reports_resolution_ok() -> None:
    response = client.get("/api/v1/modules")
    assert response.status_code == 200
    data = response.json()
    assert data["resolution_ok"] is True
    assert data["runtime_modules"][0]["pbl_id"] == "pbexamfe"
    assert [m["pbl_id"] for m in data["runtime_modules"]] == list(EXPECTED_RUNTIME_PBLS)
    assert data["load_order"] == list(EXPECTED_RUNTIME_PBLS)
    build_only_ids = [m["pbl_id"] for m in data["build_only_modules"]]
    assert "pbexamsa" in build_only_ids
    stored = next(m for m in data["build_only_modules"] if m["pbl_id"] == "pbexamsa")
    assert stored["module_id"] == "stored-procedures"
    assert all(m["status"] == "resolved" for m in data["runtime_modules"])


def test_registry_validate_resolution_matches_liblist() -> None:
    from app.modules.registry import BUILD_ONLY_MODULES, RUNTIME_MODULES, validate_resolution

    result = validate_resolution()
    assert result["resolution_ok"] is True
    assert len(RUNTIME_MODULES) == 10
    assert [m.pbl_id for m in RUNTIME_MODULES] == list(EXPECTED_RUNTIME_PBLS)
    assert [m.pbl_id for m in BUILD_ONLY_MODULES] == list(EXPECTED_BUILD_ONLY_PBLS)
    assert result["load_order"] == list(EXPECTED_RUNTIME_PBLS)


def test_migration_inventory_paths_align_with_settings() -> None:
    from app.core.config import settings

    root = settings.resolved_migration_inventory_root
    assert root.parts[-2:] == ("migration", "origin-inventory")
    assert settings.runtime_liblist_path.name == "runtime-liblist.json"
    assert settings.build_exlist_path.name == "build-exlist.json"
