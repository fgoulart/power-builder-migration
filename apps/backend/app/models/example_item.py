from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ExampleItem(Base, TimestampMixin):
    __tablename__ = "example_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

# PBBV-2 BA Gate A (remediation-84): do not extend ExampleItem for PSR catalog; see applied docs/pbbv-2-jira-specification.md.
