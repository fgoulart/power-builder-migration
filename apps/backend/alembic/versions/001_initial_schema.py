"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-10

PBBV-2 BA note (remediation-6): follow-on revision 002_psr_catalog (psr_artifacts / nested / route mappings) remains gated on the complete Jira specification in docs/pbbv-2-jira-specification.md after BA inspection of destination repo and card config.

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
