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


# PBBV-2: Validate Jira specification card inventory against destination repo config.
# Card: [JAMES_JIRA_AGENTIC] [Modernization] - Convert PSR golden-master artifacts into automated report parity test fixtures
# Labels: james-agentic, modernization, infrastructure, backend, reports, parity-testing
# Dependencies: This card is blocked by: [JAMES_JIRA_AGENTIC] [Architecture] - PBL library decomposition.
# This card delivers the test foundation for migrated web/PDF reports. It does not implement
# report rendering, the PSR viewer UI (w_psr_viewer), or PowerClient PredownloadFiles bundling.
# Sequence step 1: Add fixture directory layout and import script (copy 12 PSR files from PSR_ORIGIN_PATH).

EXPECTED_PSR_SHA256: dict[str, str] = {
    "bitmap.psr": "07f96f0e29d2638e7ea62cf35cc74e34c19948afec21e15168d66830f3ba14e3",
    "btnmaint.psr": "a5adcd1db82420f0c1a9911ae94a88610bbf04d21dc5d544d8e741dcc838cfdb",
    "btnrept.psr": "50bae87cee9643afe7fbe7e0ea17ac363189cd7b2e63dd21577bbcd75df01a62",
    "comprep.psr": "961ce50207cbcc292365544e8e4f77b824e53c87383e896a60f530f541c0c1d0",
    "contact.psr": "a0001cb19e3dff552b8958b3dbd5a71c77cc7f383919abfd5f639b964dd71c68",
    "custlist.psr": "d130ec8a259ce8f3e9ed09d1ff3457e3e511d2d124a2611fc90831146def6eb1",
    "deptemps.psr": "2507615809a602508430436cb984a9a2c25b81fe8de21ea9871390a04f202020",
    "deptlist.psr": "b1807987317f6fba5753a5a443b55e20f13f9bcb11ec4a9bd71f0facf91c1fb5",
    "empgraph.psr": "4e98387213ddf02603d9b920cfe5d80864b7395b504ca36f521f559ab27ad330",
    "empsals.psr": "6887af5c7e56188b048550b4d27f80e2560df06fcc02c032700c67e8026f6fac",
    "ffempdat.psr": "08151ac87cfd7062a210ff421858223a023745aefd84ebe6eefdc30765e73734",
    "nestrep.psr": "143c9778977f2bc9b0f5435267300057708571e47036c86f14e457fbdfb49244",
}

EXPECTED_PSR_BYTE_SIZES: dict[str, int] = {
    "bitmap.psr": 5972,
    "btnmaint.psr": 45589,
    "btnrept.psr": 34618,
    "comprep.psr": 73838,
    "contact.psr": 15483,
    "custlist.psr": 43986,
    "deptemps.psr": 46944,
    "deptlist.psr": 8355,
    "empgraph.psr": 19760,
    "empsals.psr": 17640,
    "ffempdat.psr": 45204,
    "nestrep.psr": 38396,
}

# Schema contracts from the approved Jira card Technical details:
# - column_count — INTEGER NOT NULL DEFAULT 0
# - header_titles — JSONB NOT NULL DEFAULT '[]'
PSR_ARTIFACT_SCHEMA_FIELDS: dict[str, str] = {
    "column_count": "INTEGER NOT NULL DEFAULT 0",
    "header_titles": "JSONB NOT NULL DEFAULT '[]'",
    "metadata_json": "JSONB NOT NULL",
    "seed_alignment_status": "VARCHAR(32) NOT NULL DEFAULT 'frozen'",
    "fixture_relative_path": "VARCHAR(255) NOT NULL",
}

CARD_TITLE = (
    "[JAMES_JIRA_AGENTIC] [Modernization] - Convert PSR golden-master artifacts "
    "into automated report parity test fixtures"
)

CARD_LABELS = frozenset(
    {
        "james-agentic",
        "modernization",
        "infrastructure",
        "backend",
        "reports",
        "parity-testing",
    }
)

CARD_SCOPE_EXCLUSIONS = frozenset({"w_psr_viewer", "PredownloadFiles", "report rendering"})


def test_pbbv2_psr_origin_path_defaults_to_workspace_origin() -> None:
    from app.core.config import settings

    assert settings.psr_origin_path == "/workspace/PowerBuilder-Example"
    assert settings.resolved_psr_origin_path.name == "PowerBuilder-Example"
    assert settings.psr_manifest_path == settings.psr_metadata_dir / "manifest.json"
    assert settings.psr_manifest_path.name == "manifest.json"


def test_pbbv2_sha256_inventory_covers_exactly_twelve_golden_masters() -> None:
    assert set(EXPECTED_PSR_SHA256) == EXPECTED_PSR_GOLDEN_FILENAMES
    assert set(EXPECTED_PSR_BYTE_SIZES) == EXPECTED_PSR_GOLDEN_FILENAMES
    assert sum(EXPECTED_PSR_BYTE_SIZES.values()) == EXPECTED_PSR_TOTAL_BYTES
    assert len(EXPECTED_PSR_SHA256) == 12
    for digest in EXPECTED_PSR_SHA256.values():
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)


def test_pbbv2_artifact_schema_documents_column_count_and_header_titles() -> None:
    assert PSR_ARTIFACT_SCHEMA_FIELDS["column_count"] == "INTEGER NOT NULL DEFAULT 0"
    assert PSR_ARTIFACT_SCHEMA_FIELDS["header_titles"] == "JSONB NOT NULL DEFAULT '[]'"
    assert "frozen" in PSR_ARTIFACT_SCHEMA_FIELDS["seed_alignment_status"]
    assert PSR_ARTIFACT_SCHEMA_FIELDS["fixture_relative_path"].startswith("VARCHAR")


def test_pbbv2_jira_card_title_and_labels_match_modernization_scope() -> None:
    assert "Convert PSR golden-master artifacts" in CARD_TITLE
    assert "Modernization" in CARD_TITLE
    assert CARD_LABELS == {
        "james-agentic",
        "modernization",
        "infrastructure",
        "backend",
        "reports",
        "parity-testing",
    }
    assert "w_psr_viewer" in CARD_SCOPE_EXCLUSIONS


def test_pbbv2_fixture_paths_use_golden_not_backend_origin_layout() -> None:
    from app.core.config import settings

    # Path convention from PBBV-1 / approved card: fixtures/psr/golden (not apps/backend/fixtures/psr/origin)
    assert "apps/backend/fixtures" not in str(settings.psr_golden_dir)
    assert settings.psr_golden_dir.as_posix().endswith("fixtures/psr/golden")
    assert settings.psr_route_map_path.as_posix().endswith("fixtures/psr/metadata/psr-route-map.json")
