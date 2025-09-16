from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from ..core.config import settings


engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)


def get_session() -> Generator[Session, None, None]:
    """Provide a database session dependency for FastAPI routes."""

    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Create database tables if they do not already exist."""

    SQLModel.metadata.create_all(engine)
