from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ExampleItem(Base, TimestampMixin):
    """Postgres-only demo row for destination schema (SQL Anywhere retired)."""

    __tablename__ = "example_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
