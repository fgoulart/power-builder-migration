"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-10

PBBV-2 BA note: follow-on revision 002_psr_catalog (psr_artifacts / nested / route mappings) is gated on the complete Jira specification in docs/pbbv-2-jira-specification.md.

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
