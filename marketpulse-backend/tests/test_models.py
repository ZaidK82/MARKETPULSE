from app.core.database import Base
from app import models  # noqa: F401


def test_database_models_are_registered():
    table_names = set(Base.metadata.tables.keys())

    expected_tables = {
        "stocks",
        "watchlist_items",
        "alert_rules",
        "alert_events",
        "notification_logs",
    }

    assert expected_tables.issubset(table_names)