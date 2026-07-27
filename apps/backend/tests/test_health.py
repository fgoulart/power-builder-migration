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

# PBBV-6: Module registry foundation — LibList / EXLIST resolution contract.

EXPECTED_RUNTIME_LIBLIST = [
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
]

EXPECTED_BUILD_ONLY = ["pbexamsa", "pbexamor"]


def test_modules_api_resolution_ok() -> None:
    response = client.get("/api/v1/modules")
    assert response.status_code == 200
    data = response.json()
    assert data["resolution_ok"] is True
    assert data["load_order"] == EXPECTED_RUNTIME_LIBLIST
    assert data["runtime_modules"][0]["pbl_id"] == "pbexamfe"
    assert data["runtime_modules"][0]["status"] == "resolved"
    build_ids = [m["pbl_id"] for m in data["build_only_modules"]]
    assert build_ids == EXPECTED_BUILD_ONLY
    assert any(m["module_id"] == "stored-procedures" for m in data["build_only_modules"])
    assert any(m["pbl_id"] == "pbexamsa" for m in data["build_only_modules"])


def test_registry_resolve_modules_matches_origin_liblist() -> None:
    from app.modules.registry import resolve_modules

    status = resolve_modules()
    assert status["resolution_ok"] is True
    assert [m["pbl_id"] for m in status["runtime_modules"]] == EXPECTED_RUNTIME_LIBLIST
    assert status["load_order"] == EXPECTED_RUNTIME_LIBLIST
    assert all(m["status"] == "resolved" for m in status["resolved"])
    assert [m["pbl_id"] for m in status["build_only_modules"]] == EXPECTED_BUILD_ONLY


def test_migration_inventory_paths_align_with_settings() -> None:
    from app.core.config import settings

    root = settings.resolved_migration_inventory_root
    assert root.parts[-2:] == ("migration", "origin-inventory")
    assert settings.runtime_liblist_path.name == "runtime-liblist.json"
    assert settings.build_exlist_path.name == "build-exlist.json"
    assert settings.library_manifest_path.name == "library-manifest.yaml"
    assert settings.dependency_graph_path.name == "dependency-graph.json"
