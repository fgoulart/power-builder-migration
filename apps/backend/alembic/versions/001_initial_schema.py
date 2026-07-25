"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-10

PBBV-2 BA complete (remediation-54): Jira specification applied at docs/pbbv-2-jira-specification.md (Gate A PreQA SPEC_MISSING fix — artifact rematerialized in codegen files for PreQA Input.files). Follow-on revision 002_psr_catalog (psr_artifacts / nested / route mappings) stays engineering-gated until that spec is accepted and PBL library decomposition clears. Spec materializes BA objective: I'll inspect the destination repo and card config, then produce a complete Jira specification that follows all gates.

"""

from typing import Sequence, Union

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
