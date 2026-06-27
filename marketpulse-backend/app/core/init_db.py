from app.core.database import Base, engine
from app import models  # noqa: F401


def create_db_and_tables() -> None:
    Base.metadata.create_all(bind=engine)