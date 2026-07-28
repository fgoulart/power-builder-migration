from fastapi.testclient import TestClient

from app.main import app
from app.core.config import (
    BUILD_ONLY_MODULE_CATALOG,
    EXPECTED_BUILD_EXLIST,
    EXPECTED_RUNTIME_LIBLIST,
    RUNTIME_MODULE_CATALOG,
    get_build_only_modules,
    get_runtime_modules,
    validate_runtime_resolution,
)

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


# PBBV-6: PBL LibList / module registry foundation (destination monorepo).


def test_runtime_module_count_is_ten() -> None:
    assert len(get_runtime_modules()) == 10
    assert len(RUNTIME_MODULE_CATALOG) == 10


def test_runtime_modules_match_liblist_order() -> None:
    ordered = [str(item["pbl"]) for item in get_runtime_modules()]
    assert ordered == list(EXPECTED_RUNTIME_LIBLIST)
    assert ordered[0] == "pbexamfe"
    assert [int(item["load_order"]) for item in get_runtime_modules()] == list(range(1, 11))


def test_validate_runtime_resolution_ok() -> None:
    report = validate_runtime_resolution()
    assert report["resolution_ok"] is True
    assert report["errors"] == []
    assert all(item["status"] == "resolved" for item in report["runtime_modules"])


def test_build_only_modules_excluded_from_runtime() -> None:
    runtime_pbls = {str(item["pbl"]) for item in get_runtime_modules()}
    build_only = get_build_only_modules()
    assert any(item["id"] == "stored-procedures" and item["pbl"] == "pbexamsa" for item in build_only)
    assert "pbexamsa" not in runtime_pbls
    assert "pbexamor" not in runtime_pbls
    assert len(BUILD_ONLY_MODULE_CATALOG) == 2


def test_build_exlist_matches_win32_snapshot() -> None:
    assert len(EXPECTED_BUILD_EXLIST) == 12
    assert EXPECTED_BUILD_EXLIST[5] == "pbexamsa"
    assert EXPECTED_BUILD_EXLIST[7] == "pbexamor"


def test_get_modules_returns_200() -> None:
    response = client.get("/api/v1/modules")
    assert response.status_code == 200


def test_get_modules_resolution_ok_true() -> None:
    response = client.get("/api/v1/modules")
    assert response.status_code == 200
    data = response.json()
    assert data["resolution_ok"] is True
    assert len(data["runtime_modules"]) == 10
    assert data["runtime_modules"][0]["pbl"] == "pbexamfe"
    assert data["runtime_modules"][0]["status"] == "resolved"
    assert data["runtime_modules"][0]["load_order"] == 1
    assert any(
        item["id"] == "stored-procedures" and item["pbl"] == "pbexamsa"
        for item in data["build_only_modules"]
    )
    assert data["errors"] == []
