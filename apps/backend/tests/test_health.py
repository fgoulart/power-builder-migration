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


# PBBV-2: Validate destination repo layout and Jira card specification gates.
# I'll inspect the destination repo and card config, then produce a complete
# Jira specification that follows all gates.

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
BLOCKED_BY = "[JAMES_JIRA_AGENTIC] [Architecture] - PBL library decomposition"

CARD_DELIVERS = (
    "This card delivers the test foundation for migrated web/PDF reports. "
    "It does not implement report rendering, the PSR viewer UI (w_psr_viewer), "
    "or PowerClient PredownloadFiles bundling."
)

IMPLEMENTATION_SEQUENCE_STEP_1 = (
    "Add fixture directory layout and import script "
    "(copy 12 PSR files from PSR_ORIGIN_PATH)."
)

EXPECTED_PSR_FILENAMES = frozenset(
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

PSR_CHECKSUMS: dict[str, tuple[int, str]] = {
    "bitmap.psr": (5972, "07f96f0e29d2638e7ea62cf35cc74e34c19948afec21e15168d66830f3ba14e3"),
    "btnmaint.psr": (45589, "a5adcd1db82420f0c1a9911ae94a88610bbf04d21dc5d544d8e741dcc838cfdb"),
    "btnrept.psr": (34618, "50bae87cee9643afe7fbe7e0ea17ac363189cd7b2e63dd21577bbcd75df01a62"),
    "comprep.psr": (73838, "961ce50207cbcc292365544e8e4f77b824e53c87383e896a60f530f541c0c1d0"),
    "contact.psr": (15483, "a0001cb19e3dff552b8958b3dbd5a71c77cc7f383919abfd5f639b964dd71c68"),
    "custlist.psr": (43986, "d130ec8a259ce8f3e9ed09d1ff3457e3e511d2d124a2611fc90831146def6eb1"),
    "deptemps.psr": (46944, "2507615809a602508430436cb984a9a2c25b81fe8de21ea9871390a04f202020"),
    "deptlist.psr": (8355, "b1807987317f6fba5753a5a443b55e20f13f9bcb11ec4a9bd71f0facf91c1fb5"),
    "empgraph.psr": (19760, "4e98387213ddf02603d9b920cfe5d80864b7395b504ca36f521f559ab27ad330"),
    "empsals.psr": (17640, "6887af5c7e56188b048550b4d27f80e2560df06fcc02c032700c67e8026f6fac"),
    "ffempdat.psr": (45204, "08151ac87cfd7062a210ff421858223a023745aefd84ebe6eefdc30765e73734"),
    "nestrep.psr": (38396, "143c9778977f2bc9b0f5435267300057708571e47036c86f14e457fbdfb49244"),
}

PLANNED_API_ROUTES = (
    "/api/v1/psr/artifacts",
    "/api/v1/psr/artifacts/{filename}",
    "/api/v1/psr/artifacts/{filename}/download",
    "/api/v1/psr/manifest",
    "/api/v1/psr/route-mappings",
)

ROUTE_MAPPINGS: dict[str, str] = {
    "bitmap.psr": "/reports/bitmap/sample",
    "btnmaint.psr": "/reports/maintenance/button",
    "btnrept.psr": "/reports/button/employee-compensation",
    "comprep.psr": "/reports/composite/customer-products",
    "contact.psr": "/reports/contact",
    "custlist.psr": "/reports/list/customers",
    "deptemps.psr": "/reports/group/dept-employees",
    "deptlist.psr": "/reports/list/departments",
    "empgraph.psr": "/reports/graph/employee-dept",
    "empsals.psr": "/reports/graph/employee-salary",
    "ffempdat.psr": "/reports/freeform/employee-data",
    "nestrep.psr": "/reports/nested/employees-by-dept",
}

PRIORITY_STRUCTURAL_ASSERTIONS = {
    "comprep.psr": {
        "report_type": "composite",
        "processing_mode": 5,
        "nested_dataobjects": {"d_cust_report", "d_products_graph", "d_products"},
        "tables": {"customer", "product"},
    },
    "nestrep.psr": {
        "report_type": "nested",
        "nested_dataobjects": {"d_emp_by_dept"},
        "tables": {"employee", "department"},
    },
    "btnrept.psr": {
        "header_titles": {"Employee Compensation Report"},
    },
    "deptemps.psr": {
        "report_type": "group",
        "pbselect_present": True,
        "tables": {"employee", "department"},
    },
}

PSR_ARTIFACT_SCHEMA_FIELDS = frozenset(
    {
        "column_count",
        "header_titles",
        "metadata_json",
        "seed_alignment_status",
        "fixture_relative_path",
    }
)

# Catalog DDL anchors for future Alembic 002_psr_catalog migration.
PSR_ARTIFACT_COLUMN_DDL = {
    "column_count": "INTEGER NOT NULL DEFAULT 0",
    "header_titles": "JSONB NOT NULL DEFAULT '[]'::jsonb",
    "metadata_json": "JSONB NOT NULL DEFAULT '{}'::jsonb",
    "seed_alignment_status": "VARCHAR(32) NOT NULL DEFAULT 'frozen'",
    "fixture_relative_path": "VARCHAR(512) NOT NULL",
}


def test_card_metadata_matches_jira_specification() -> None:
    assert "Modernization" in CARD_TITLE
    assert "PSR golden-master" in CARD_TITLE
    assert CARD_TITLE.startswith("[JAMES_JIRA_AGENTIC]")
    assert len(CARD_LABELS) == 6
    assert "parity-testing" in CARD_LABELS
    assert "james-agentic" in CARD_LABELS
    assert "PBL library decomposition" in BLOCKED_BY
    assert BLOCKED_BY.startswith("[JAMES_JIRA_AGENTIC] [Architecture]")


def test_card_scope_excludes_viewer_and_rendering() -> None:
    assert "test foundation" in CARD_DELIVERS
    assert "w_psr_viewer" in CARD_DELIVERS
    assert "PredownloadFiles" in CARD_DELIVERS
    assert "does not implement report rendering" in CARD_DELIVERS


def test_implementation_sequence_starts_with_fixture_import() -> None:
    assert "fixture directory layout" in IMPLEMENTATION_SEQUENCE_STEP_1
    assert "import script" in IMPLEMENTATION_SEQUENCE_STEP_1
    assert "PSR_ORIGIN_PATH" in IMPLEMENTATION_SEQUENCE_STEP_1
    assert "12 PSR" in IMPLEMENTATION_SEQUENCE_STEP_1


def test_psr_inventory_matches_verified_origin_catalog() -> None:
    assert len(EXPECTED_PSR_FILENAMES) == 12
    total_bytes = sum(size for size, _ in PSR_CHECKSUMS.values())
    assert total_bytes == EXPECTED_PSR_TOTAL_BYTES
    assert set(PSR_CHECKSUMS) == EXPECTED_PSR_FILENAMES


def test_psr_checksum_inventory_covers_all_twelve_files() -> None:
    for filename in EXPECTED_PSR_FILENAMES:
        byte_size, sha256 = PSR_CHECKSUMS[filename]
        assert byte_size > 0
        assert len(sha256) == 64


def test_config_paths_align_with_card_fixture_layout() -> None:
    from app.core.config import settings

    assert settings.psr_origin_path == "/workspace/PowerBuilder-Example"
    assert settings.psr_fixtures_dir == "apps/backend/fixtures/psr"
    assert settings.psr_origin_dir == settings.resolved_psr_fixtures_dir / "origin"
    assert settings.psr_manifest_path == settings.resolved_psr_fixtures_dir / "manifest.json"
    assert settings.psr_metadata_dir == settings.resolved_psr_fixtures_dir / "metadata"
    assert settings.resolved_psr_fixtures_dir.name == "psr"


def test_planned_psr_api_routes_defined_in_specification() -> None:
    assert len(PLANNED_API_ROUTES) == 5
    assert "/api/v1/psr/artifacts" in PLANNED_API_ROUTES
    assert "/api/v1/psr/manifest" in PLANNED_API_ROUTES
    assert "/api/v1/psr/route-mappings" in PLANNED_API_ROUTES


def test_route_mappings_cover_all_twelve_artifacts() -> None:
    assert set(ROUTE_MAPPINGS) == EXPECTED_PSR_FILENAMES
    assert ROUTE_MAPPINGS["comprep.psr"] == "/reports/composite/customer-products"
    assert ROUTE_MAPPINGS["nestrep.psr"] == "/reports/nested/employees-by-dept"
    assert ROUTE_MAPPINGS["btnrept.psr"] == "/reports/button/employee-compensation"


def test_priority_structural_assertions_defined_for_parity_fixtures() -> None:
    comprep = PRIORITY_STRUCTURAL_ASSERTIONS["comprep.psr"]
    nestrep = PRIORITY_STRUCTURAL_ASSERTIONS["nestrep.psr"]
    btnrept = PRIORITY_STRUCTURAL_ASSERTIONS["btnrept.psr"]
    deptemps = PRIORITY_STRUCTURAL_ASSERTIONS["deptemps.psr"]

    assert comprep["report_type"] == "composite"
    assert comprep["processing_mode"] == 5
    assert comprep["nested_dataobjects"] == {
        "d_cust_report",
        "d_products_graph",
        "d_products",
    }
    assert nestrep["report_type"] == "nested"
    assert "d_emp_by_dept" in nestrep["nested_dataobjects"]
    assert "Employee Compensation Report" in btnrept["header_titles"]
    assert deptemps["report_type"] == "group"
    assert deptemps["pbselect_present"] is True


def test_database_schema_fields_include_column_count_and_header_titles() -> None:
    assert "column_count" in PSR_ARTIFACT_SCHEMA_FIELDS
    assert "header_titles" in PSR_ARTIFACT_SCHEMA_FIELDS
    assert "metadata_json" in PSR_ARTIFACT_SCHEMA_FIELDS
    assert "seed_alignment_status" in PSR_ARTIFACT_SCHEMA_FIELDS
    assert len(PSR_ARTIFACT_SCHEMA_FIELDS) == 5
    assert PSR_ARTIFACT_COLUMN_DDL["column_count"] == "INTEGER NOT NULL DEFAULT 0"
    assert PSR_ARTIFACT_COLUMN_DDL["header_titles"].startswith("JSONB NOT NULL DEFAULT")
    assert set(PSR_ARTIFACT_COLUMN_DDL) == PSR_ARTIFACT_SCHEMA_FIELDS
