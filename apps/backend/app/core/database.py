from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _assert_postgres_only(url: str) -> None:
    normalized = url.split("://", 1)[0].lower()
    if not normalized.startswith("postgresql") and normalized != "postgres":
        raise ValueError(
            "Postgres-only destination runtime: SQL Anywhere is origin-only and retired here."
        )


_assert_postgres_only(settings.database_url)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,
    pool_timeout=min(settings.transaction_timeout_seconds, 30),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
